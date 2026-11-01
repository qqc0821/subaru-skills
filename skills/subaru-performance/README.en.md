# subaru-performance

Turn a recorded page load into a local interactive main-thread report: scripts, long tasks, resource timing and LCP.

> Use $subaru-performance to profile this URL and show which scripts occupy the main thread before and after LCP.

Alternatively provide an uncompressed Chrome Performance JSON for offline analysis. Execution attribution is evidence, not proof of every loading bottleneck. Worker and iframe execution are excluded.

Requires Python 3.10+. Live capture optionally uses ego-browser. The generated HTML has no external dependencies.
