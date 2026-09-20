#!/usr/bin/env python3
"""Detect visual artifacts in *rendered* slide images (pixel-level QA).

Standard library only, read-only, offline.  This is the raster half of the
deliverable QA gate: the host's PPTX inspection reads XML geometry, this script
reads the pixels a human actually sees.  It covers the three defect families that
keep slipping through geometry-only review:

  * ``wrapped-numbers``  a numeral group broken across lines ("8-10" rendering as
    "8-1" / "0"), with the orphan inflated by shrink-to-fit;
  * ``oversized-glyph``  a glyph far taller than its line neighbours, the same
    defect once it is already built;
  * ``band-cut``         a thin straight band running through a hard colour
    boundary, reading as a floating hairline in a gutter.

It deliberately does NOT guess z-order: from pixels alone, a line hidden behind a
shape and a line that legitimately ends at a shape's edge look identical.  That
case is covered by authoring rules and the human checklist instead.

Findings carry measurable evidence (bounding boxes, colours, pixel counts) and
are estimates, not verdicts: treat them as "look at this page full size".

Usage:
    python3 detect_pixel_artifacts.py slide-03.png
    python3 detect_pixel_artifacts.py renders/ --json
    python3 detect_pixel_artifacts.py renders/ --detail
    python3 detect_pixel_artifacts.py --doctor
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path
CHECK = "detect_pixel_artifacts"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


# --------------------------------------------------------------------------- #
# Colour handling
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RGB:
    r: int
    g: int
    b: int

    def hex(self) -> str:
        return "#%02x%02x%02x" % (self.r, self.g, self.b)


def _dist(a: RGB, b: RGB) -> float:
    """Perceptual-ish distance; weights keep near-greys from merging with accents."""
    dr, dg, db = a.r - b.r, a.g - b.g, a.b - b.b
    return math.sqrt((2 * dr * dr) + (4 * dg * dg) + (3 * db * db))


class Scale:
    """Map true colour to a small palette of exact colours.

    Anti-aliased pixels are mapped to the nearest palette entry; we keep the
    *exact* mapping so a re-mapped pixel never introduces a third colour.
    """

    def __init__(self, tolerance: float = 46.0):
        self.tolerance = tolerance
        self.colors: list[RGB] = []
        self._cache: dict[int, int] = {}

    def index(self, r: int, g: int, b: int) -> int:
        key = (r << 16) | (g << 8) | b
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        px = RGB(r, g, b)
        best, best_d = -1, self.tolerance
        for i, c in enumerate(self.colors):
            d = _dist(px, c)
            if d < best_d:
                best, best_d = i, d
        if best < 0:
            self.colors.append(px)
            best = len(self.colors) - 1
        self._cache[key] = best
        return best

    def palette(self) -> list[RGB]:
        return list(self.colors)


# --------------------------------------------------------------------------- #
# Minimal PNG decoder (8-bit non-interlaced, the only thing renderers emit)
# --------------------------------------------------------------------------- #
@dataclass
class Image:
    width: int
    height: int
    rgb: bytearray  # width*height*3
    path: Path

    def px(self, x: int, y: int) -> tuple[int, int, int]:
        i = (y * self.width + x) * 3
        return self.rgb[i], self.rgb[i + 1], self.rgb[i + 2]


class PNGError(RuntimeError):
    pass


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def read_png(path: Path) -> Image:
    data = path.read_bytes()
    if data[:8] != PNG_MAGIC:
        raise PNGError(f"{path}: not a PNG file")
    pos, idat = 8, bytearray()
    width = height = depth = ctype = interlace = 0
    plte: list[RGB] = []
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype_name = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if ctype_name == b"IHDR":
            width, height, depth, ctype, _comp, _filt, interlace = struct.unpack(">IIBBBBB", body[:13])
        elif ctype_name == b"PLTE":
            plte = [RGB(body[i], body[i + 1], body[i + 2]) for i in range(0, len(body) - 2, 3)]
        elif ctype_name == b"IDAT":
            idat += body
        elif ctype_name == b"IEND":
            break
        pos += 12 + length
    if interlace:
        raise PNGError(f"{path}: interlaced PNG is not supported (renderers emit non-interlaced)")
    if depth != 8:
        raise PNGError(f"{path}: only 8-bit PNG is supported (got {depth}-bit)")
    if ctype not in (0, 2, 3, 4, 6):
        raise PNGError(f"{path}: unsupported colour type {ctype}")

    channels = CHANNELS[ctype]
    stride = width * channels
    raw = zlib.decompress(bytes(idat))
    expected = height * (stride + 1)
    if len(raw) < expected:
        raise PNGError(f"{path}: truncated image data")
    out = bytearray(width * height * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        ftype = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if ftype == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                c = prev[i - channels] if i >= channels else 0
                line[i] = (line[i] + _paeth(a, prev[i], c)) & 0xFF
        elif ftype != 0:
            raise PNGError(f"{path}: unknown filter type {ftype} on row {y}")
        base_out = y * width * 3
        if ctype == 2:
            out[base_out:base_out + width * 3] = line
        elif ctype == 6:
            for x in range(width):
                s = x * 4
                out[base_out + x * 3:base_out + x * 3 + 3] = line[s:s + 3]
        elif ctype == 0:
            for x in range(width):
                v = line[x]
                out[base_out + x * 3] = out[base_out + x * 3 + 1] = out[base_out + x * 3 + 2] = v
        elif ctype == 4:
            for x in range(width):
                v = line[x * 2]
                out[base_out + x * 3] = out[base_out + x * 3 + 1] = out[base_out + x * 3 + 2] = v
        elif ctype == 3:
            for x in range(width):
                idx = line[x]
                c = plte[idx] if idx < len(plte) else RGB(0, 0, 0)
                out[base_out + x * 3] = c.r
                out[base_out + x * 3 + 1] = c.g
                out[base_out + x * 3 + 2] = c.b
        prev = line
    return Image(width, height, out, path)


# --------------------------------------------------------------------------- #
# Raster model
# --------------------------------------------------------------------------- #
@dataclass
class Raster:
    """Quantised view of an image: class index per pixel plus the palette."""

    img: Image
    classes: bytearray  # one class index per pixel (0..254)
    palette: list[RGB]
    background: int  # palette index of the modal border/background colour

    @property
    def width(self) -> int:
        return self.img.width

    @property
    def height(self) -> int:
        return self.img.height

    def at(self, x: int, y: int) -> int:
        return self.classes[y * self.width + x]

    def hex(self, idx: int) -> str:
        return self.palette[idx].hex()


def build_raster(path: Path, tolerance: float = 46.0) -> Raster:
    img = read_png(path)
    scale = Scale(tolerance=tolerance)
    classes = bytearray(scale.index(*img.px(x, y)) for y in range(img.height) for x in range(img.width))
    palette = scale.palette()
    if len(palette) > 255:
        # Extremely rare with a 46-distance tolerance; fall back to the modal colours.
        counts: dict[int, int] = {}
        for c in classes:
            counts[c] = counts.get(c, 0) + 1
        keep = [i for i, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:255]]
        remap = {old: new for new, old in enumerate(keep)}
        classes = bytearray(remap.get(c, 0) for c in classes)
        palette = [palette[i] for i in keep]
    # The page/void colour is the modal colour: screenshot frames and window
    # chrome are not part of the slide, and a border sample would pick those up.
    counts: dict[int, int] = {}
    for c in classes:
        counts[c] = counts.get(c, 0) + 1
    background = max(counts, key=lambda k: counts[k]) if counts else 0
    return Raster(img, classes, palette, background)


# --------------------------------------------------------------------------- #
# Findings
# --------------------------------------------------------------------------- #
@dataclass
class Artifact:
    key: str
    severity: str
    message: str
    detail: dict = field(default_factory=dict)


@dataclass
class Finding:
    """One reported artifact.  The key carries the file name and line so a host
    that baselines findings can suppress them per slide."""

    key: str
    message: str
    path: str
    line: int
    severity: str


def _finding(path: Path, a: Artifact) -> Finding:
    key = f"{a.key}:{path.name}:l{a.detail.get('line', 0)}"
    return Finding(key, a.message, str(path), a.detail.get("line", 0), a.severity)


# --------------------------------------------------------------------------- #
# Detector 1 - occluded line ends
# --------------------------------------------------------------------------- #

def _row_runs(rast: Raster, y: int, min_len: int, bg: int) -> list[tuple[int, int, int]]:
    """Non-background runs in one row: (start, end, class)."""
    runs: list[tuple[int, int, int]] = []
    x = 0
    w = rast.width
    row = y * w
    while x < w:
        cls = rast.classes[row + x]
        if cls == bg:
            x += 1
            continue
        start = x
        while x < w and rast.classes[row + x] == cls:
            x += 1
        if x - start >= min_len:
            runs.append((start, x - 1, cls))
    return runs



def _color_run(rast: Raster, y: int, x: int, cls: int | None = None) -> int:
    """Length of the run of ``cls`` (default: the colour at x) through ``x`` in row y."""
    cls = rast.at(x, y) if cls is None else cls
    left = right = x
    while left - 1 >= 0 and rast.at(left - 1, y) == cls:
        left -= 1
    while right + 1 < rast.width and rast.at(right + 1, y) == cls:
        right += 1
    return right - left + 1


def detect_band_cuts(rast: Raster, max_band: int = 40, min_height: int = 10,
                     min_field: int = 150) -> list[Artifact]:
    """A thin band crossing a hard, long colour boundary.

    Requires a genuinely large boundary: two colour fields at least ``min_field``
    wide on both sides of a vertical band.  Text anti-aliasing creates short
    boundaries (a glyph stroke), so this size gate is what keeps the heuristic
    quiet on ordinary pages.
    """
    w, h, bg = rast.width, rast.height, rast.background
    candidates: list[tuple[int, int, int]] = []
    for y in range(h):
        for (x0, x1, cls) in _row_runs(rast, y, 2, bg):
            if x1 - x0 + 1 > max_band:
                continue
            # the band's own colour must not be the field colour
            if _color_run(rast, y, x0 - 1) >= min_field:
                candidates.append((x0, x1, y))
    if not candidates:
        return []

    groups: list[dict] = []
    for (x0, x1, y) in candidates:
        for g in groups:
            if abs(g["x0"] - x0) <= 2 and abs(g["x1"] - x1) <= 2 and y - g["y1"] <= 3:
                g["y1"] = y
                break
        else:
            groups.append({"x0": x0, "x1": x1, "y0": y, "y1": y})

    out: list[Artifact] = []
    for g in groups:
        height = g["y1"] - g["y0"] + 1
        if height < min_height:
            continue
        xm = (g["x0"] + g["x1"]) // 2
        cls = rast.at(xm, (g["y0"] + g["y1"]) // 2)
        probe = g["x0"] - 4
        if probe < 0:
            continue
        above = rast.at(probe, g["y0"])
        below = rast.at(probe, g["y1"])
        if above == below or above == cls or below == cls or below == bg:
            continue
        field = min(_color_run(rast, g["y0"], probe, above),
                    _color_run(rast, g["y1"], probe, below))
        if field < min_field:
            continue
        out.append(Artifact(
            "band-cut", "warning",
            f"{g['x1'] - g['x0'] + 1}px {rast.hex(cls)} band crosses a {field}px "
            f"{rast.hex(above)}/{rast.hex(below)} boundary over {height}px",
            {"line": g["y0"] + 1,
             "bbox": [g["x0"], g["y0"], g["x1"] - g["x0"] + 1, height],
             "band_color": rast.hex(cls), "above_color": rast.hex(above),
             "below_color": rast.hex(below), "crossing_px": height,
             "field_px": field}))
    return out


# --------------------------------------------------------------------------- #
# Detector 3 - axis-aligned lines that secretly drift
# --------------------------------------------------------------------------- #
def _ink_components(rast: Raster) -> list[tuple[int, int, int, int, int]]:
    """Connected components of non-background ink: (x, y, w, h, pixels)."""
    w, h, bg = rast.width, rast.height, rast.background
    seen = bytearray(w * h)
    comps: list[tuple[int, int, int, int, int]] = []
    for y0 in range(h):
        row = y0 * w
        for x0 in range(w):
            i = row + x0
            if seen[i] or rast.classes[i] == bg:
                continue
            stack = [(x0, y0)]
            seen[i] = 1
            minx = maxx = x0
            miny = maxy = y0
            count = 0
            while stack:
                x, y = stack.pop()
                count += 1
                minx, maxx = min(minx, x), max(maxx, x)
                miny, maxy = min(miny, y), max(maxy, y)
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not seen[j] and rast.classes[j] != bg:
                            seen[j] = 1
                            stack.append((nx, ny))
            if count > 20:
                comps.append((minx, miny, maxx - minx + 1, maxy - miny + 1, count))
    return comps


def detect_wrapped_numbers(rast: Raster, min_height: int = 40,
                           gap_max: int = 80) -> list[Artifact]:
    """A numeral group broken across lines ("8-10" rendering as "8-1" / "0").

    Baselines are the component bottoms clustered along y.  An ink block that
    starts a fresh baseline and touches a component on the baseline above it is a
    wrap inside one logical line - the orphan grows because the box shrank to fit.
    """
    comps = _ink_components(rast)
    if not comps:
        return []
    tall = [c for c in comps if c[3] >= min_height]
    if len(tall) < 2:
        return []
    out: list[Artifact] = []
    for (x, y, cw, ch, _n) in tall:
        bottom = y + ch
        above = [c for c in tall
                 if (c[0], c[1], c[2], c[3]) != (x, y, cw, ch)
                 and (c[1] + c[3]) < y and y - (c[1] + c[3]) <= gap_max]
        if not above:
            continue
        # the orphan must sit between the horizontal extent of the group above it
        for (ax, ay, aw, ah, _) in above:
            if aw >= 8 * cw or cw >= 8 * aw:
                continue
            if ax - cw <= x <= ax + aw + cw:
                out.append(Artifact(
                    "wrapped-numbers", "warning",
                    f"{ch}px ink block starts a new baseline {y - (ay + ah)}px below a "
                    f"{aw}px group while overlapping it horizontally - a numeric group "
                    f"wrapped inside its box",
                    {"line": y + 1, "bbox": [x, y, cw, ch],
                     "orphan_height_px": ch, "above_width_px": aw,
                     "above_bottom": ay + ah, "gap_px": y - (ay + ah)}))
                break
    return out


def detect_glyph_scale(rast: Raster, min_height: int = 80, ratio: float = 3.0) -> list[Artifact]:
    """A glyph far taller than its line neighbours.

    Only extreme ratios qualify: a CJK title next to a small Latin label is
    legitimate typography, an 8x-tall orphan numeral is not.
    """
    comps = _ink_components(rast)
    out: list[Artifact] = []
    big = [c for c in comps if c[3] >= min_height]
    for (x, y, cw, ch, _n) in big:
        same_line = [c[3] for c in comps
                     if (c[0], c[1], c[2], c[3]) != (x, y, cw, ch)
                     and abs((c[1] + c[3]) - (y + ch)) <= 4 and c[3] < ch]
        if not same_line:
            continue
        typical = sorted(same_line)[len(same_line) // 2]
        if typical and ch / typical >= ratio:
            out.append(Artifact(
                "oversized-glyph", "warning",
                f"{ch}px glyph is {ch / typical:.1f}x taller than its line neighbours "
                f"({typical}px) - text wrapped or shrank to fit its box",
                {"line": y + 1, "bbox": [x, y, cw, ch], "glyph_height_px": ch,
                 "neighbour_height_px": typical}))
    return out


# Default detectors are the ones whose evidence is measurable and stable.
# ``wrapped-numbers`` is a stronger sibling of ``oversized-glyph`` and is kept
# separate so a deck can gate on it without the weaker heuristic.
DETECTORS = {
    "wrapped-numbers": detect_wrapped_numbers,
    "oversized-glyph": detect_glyph_scale,
    "band-cut": detect_band_cuts,
}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def analyze(path: Path, tolerance: float = 46.0, only: set[str] | None = None) -> list[Artifact]:
    rast = build_raster(path, tolerance)
    found: list[Artifact] = []
    active = {n: f for n, f in DETECTORS.items() if not only or n in only}
    for fn in active.values():
        found.extend(fn(rast))
    found.sort(key=lambda a: (a.detail.get("line", 0), a.key))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect rendering artifacts in slide PNGs (pixel-level QA)")
    parser.add_argument("png", nargs="*", help="PNG file(s) or a directory of renders")
    parser.add_argument("--detail", action="store_true", help="include measurement detail for each finding")
    parser.add_argument("--doctor", action="store_true",
                        help="list the detector families and their known limits")
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero when warnings were found")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    if args.doctor:
        print("detect_pixel_artifacts: stdlib only, no external dependencies")
        for name in sorted(DETECTORS):
            print(f"  [detector] {name}")
        print("limits: these are heuristics that confirm geometry, not intent;")
        print("        they cannot tell what draws over what (z-order).")
        return 0
    if not args.png:
        parser.error("provide at least one PNG file or directory")
    targets: list[Path] = []
    for raw in args.png:
        p = Path(raw)
        if not p.exists():
            print(f"detect_pixel_artifacts: file not found: {raw}", file=sys.stderr)
            return 2
        targets.extend(sorted(p.rglob("*.png")) if p.is_dir() else [p])
    if not targets:
        print("detect_pixel_artifacts: no PNG found", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for p in targets:
        try:
            artifacts = analyze(p)
        except PNGError as exc:
            print(f"detect_pixel_artifacts: {exc}", file=sys.stderr)
            return 2
        for a in artifacts:
            findings.append(_finding(p, a))
        if not args.json:
            print(f"{p.name}: {len(artifacts)} finding(s)")
            for a in artifacts:
                extra = "  " + json.dumps(a.detail, ensure_ascii=False) if args.detail else ""
                print(f"  [{a.severity}] {a.key} @line {a.detail.get('line', 0)}: {a.message}{extra}")

    if args.json:
        print(json.dumps({
            "check": CHECK,
            "findings": [{"key": f.key, "severity": f.severity, "path": f.path,
                          "line": f.line, "message": f.message} for f in findings],
        }, ensure_ascii=False, indent=2))
    elif not findings:
        print("  OK - no artifacts found")
    warnings = [f for f in findings if f.severity == "warning"]
    errors = [f for f in findings if f.severity == "error"]
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
