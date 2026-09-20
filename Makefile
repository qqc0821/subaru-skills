PYTHON ?= python3

.PHONY: help check check-skills check-links check-consistency check-assets check-style-system check-style-router check-context-budget check-installability doctor baseline test eval eval-clean new-task hooks validate render montage lint-copy pixel-qa new-style style-router

help:
	@echo "subaru-skills harness"
	@echo "  make check     run all harness checks (shared quality-gate entry)"
	@echo "  make doctor    environment capability probe"
	@echo "  make baseline  record current findings as known baseline"
	@echo "  make test      compile tools and smoke-test doctor"
	@echo "  make eval      run the eval harness and enforce coverage policy"
	@echo "  make eval-clean rebuild deterministic fixtures on a clean checkout, then enforce the clean policy"
	@echo "  make new-task  scaffold task_plan/findings/progress from docs/templates/"
	@echo "  make hooks     install the make check pre-commit hook"
	@echo "  make validate  validate a deck:  PPTX=path/to/deck.pptx"
	@echo "  make render    render a deck:    PPTX=... [OUT=dir]"
	@echo "  make montage   contact sheet:    DIR=slides/ [OUT=file]"
	@echo "  make lint-copy copy lint:        SRC=deck.pptx|outline.md"
	@echo "  make pixel-qa  render QA:        DIR=renders/"
	@echo "  make new-style scaffold a style: ID=x NAME=... [REGISTER=1]"
	@echo "  make style-router regenerate styles/router.md from styles/index.json"

check:
	@PYTHON="$(PYTHON)" sh tools/check.sh

check-skills:
	@$(PYTHON) tools/validate_skills.py --baseline tools/baseline.json
check-links:
	@$(PYTHON) tools/check_links.py --baseline tools/baseline.json
check-consistency:
	@$(PYTHON) tools/check_consistency.py --baseline tools/baseline.json
check-assets:
	@$(PYTHON) tools/check_assets.py --baseline tools/baseline.json
check-style-system:
	@$(PYTHON) tools/check_style_system.py --baseline tools/baseline.json
check-style-router:
	@$(PYTHON) tools/gen_style_router.py --baseline tools/baseline.json
check-context-budget:
	@$(PYTHON) tools/check_context_budget.py --baseline tools/baseline.json
check-installability:
	@$(PYTHON) tools/check_installability.py --baseline tools/baseline.json

doctor:
	@$(PYTHON) tools/doctor.py

baseline:
	@for c in validate_skills check_links check_consistency check_assets check_style_system check_installability; do \
		$(PYTHON) tools/$$c.py --update-baseline --baseline tools/baseline.json; \
	done
	@$(PYTHON) tools/gen_style_router.py --update-baseline --baseline tools/baseline.json
	@$(PYTHON) tools/check_context_budget.py --update-baseline --baseline tools/baseline.json

test:
	@$(PYTHON) -m compileall -q tools && echo "compileall: OK"
	@$(PYTHON) tools/doctor.py --json > /dev/null && echo "doctor: OK"
	@$(PYTHON) tools/validate_pptx.py --help > /dev/null && echo "validate_pptx: OK"
	@$(PYTHON) skills/subaru-slides/scripts/detect_fonts.py --doctor > /dev/null && echo "detect_fonts: OK"
	@$(PYTHON) tools/render_preview.py --check > /dev/null && echo "render_preview: OK"
	@$(PYTHON) tools/make_montage.py --help > /dev/null && echo "make_montage: OK"
	@$(PYTHON) tools/prepare_eval_artifacts.py --help > /dev/null && echo "prepare_eval_artifacts: OK"
	@$(PYTHON) -m unittest discover -s tests

eval:
	@$(PYTHON) tools/run_evals.py

eval-clean:
	@$(PYTHON) tools/prepare_eval_artifacts.py --artifacts-dir evals/results/clean-artifacts
	@$(PYTHON) tools/run_evals.py --artifacts-dir evals/results/clean-artifacts --policy evals/policy-clean.json --environment evals/environment-clean.json

new-task:
	@sh tools/new_task.sh

hooks:
	@sh tools/install-hooks.sh

validate:
	@test -n "$(PPTX)" || (echo "usage: make validate PPTX=path/to/deck.pptx"; exit 2)
	@$(PYTHON) tools/validate_pptx.py "$(PPTX)"

render:
	@test -n "$(PPTX)" || (echo "usage: make render PPTX=... [OUT=dir]"; exit 2)
	@$(PYTHON) tools/render_preview.py "$(PPTX)" $(if $(OUT),--out-dir "$(OUT)")

lint-copy:
	@test -n "$(SRC)" || (echo "usage: make lint-copy SRC=deck.pptx|outline.md"; exit 2)
	@$(PYTHON) tools/lint_copy.py "$(SRC)"

pixel-qa:
	@test -n "$(DIR)" || (echo "usage: make pixel-qa DIR=renders/"; exit 2)
	@$(PYTHON) skills/subaru-slides/scripts/detect_pixel_artifacts.py --detail "$(DIR)"

new-style:
	@test -n "$(ID)" -a -n "$(NAME)" || (echo "usage: make new-style ID=x NAME=\"...\" [REGISTER=1]"; exit 2)
	@$(PYTHON) tools/new_style.py "$(ID)" --name "$(NAME)" $(if $(REGISTER),--register)

style-router:
	@$(PYTHON) tools/gen_style_router.py --write

montage:
	@test -n "$(DIR)" || (echo "usage: make montage DIR=slides/ [OUT=file]"; exit 2)
	@if command -v uv >/dev/null 2>&1; then uv run --quiet tools/make_montage.py --input-dir "$(DIR)" $(if $(OUT),--out "$(OUT)") || $(PYTHON) tools/make_montage.py --input-dir "$(DIR)" $(if $(OUT),--out "$(OUT)"); else $(PYTHON) tools/make_montage.py --input-dir "$(DIR)" $(if $(OUT),--out "$(OUT)"); fi
