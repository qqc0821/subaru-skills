PYTHON ?= python3

.PHONY: help check check-skills check-links check-consistency check-assets check-style-system doctor baseline test eval new-task hooks

help:
	@echo "subaru-skills harness"
	@echo "  make check     run all harness checks (same entry as CI)"
	@echo "  make doctor    environment capability probe"
	@echo "  make baseline  record current findings as known baseline"
	@echo "  make test      compile tools and smoke-test doctor"
	@echo "  make eval      run the eval harness (skips cases without artifacts)"
	@echo "  make new-task  scaffold task_plan/findings/progress from docs/templates/"
	@echo "  make hooks     install the make check pre-commit hook"

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

doctor:
	@$(PYTHON) tools/doctor.py

baseline:
	@for c in validate_skills check_links check_consistency check_assets check_style_system; do \
		$(PYTHON) tools/$$c.py --update-baseline --baseline tools/baseline.json; \
	done

test:
	@$(PYTHON) -m compileall -q tools && echo "compileall: OK"
	@$(PYTHON) tools/doctor.py --json > /dev/null && echo "doctor: OK"

eval:
	@$(PYTHON) tools/run_evals.py

new-task:
	@sh tools/new_task.sh

hooks:
	@sh tools/install-hooks.sh
