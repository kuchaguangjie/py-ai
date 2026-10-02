# ============================================================================
# py-ai — developer Makefile
# ----------------------------------------------------------------------------
# A tiny task runner around `uv` (dependency + virtualenv management).
# Run `make` or `make help` to list every available target.
# ============================================================================

# --- Configurable variables -------------------------------------------------
UV      ?= uv                     # uv executable
MAIN    ?= main.py                # primary entry point (demo dispatcher)
DEMO    ?= py_basic/type_hints_demo.py  # standalone demo module
RUN     ?= $(UV) run              # execute a script in the project venv

# --- Helpers ----------------------------------------------------------------
# List targets that carry a `## comment` as self-documenting help.
define HELP
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; \
		       {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
endef

.DEFAULT_GOAL := help
.PHONY: help sync install run demo list test check typecheck clean distclean

# ============================================================================
# Targets
# ============================================================================

help: ## Show this help message
	@echo "py-ai — available make targets:"
	$(HELP)

sync: ## Create/update the virtualenv from uv.lock (incl. dev deps)
	$(UV) sync

install: sync ## Alias for `sync`

run: ## Run every registered demo via the main dispatcher
	$(RUN) $(MAIN)

list: ## List the demos registered in main.py
	$(RUN) $(MAIN) --list

demo: ## Run the type-hints demo module directly
	$(RUN) $(DEMO)

test: ## Run the test suite with pytest
	$(UV) run pytest

check typecheck: ## Static type-check the project with pyright
	$(UV) run pyright

clean: ## Remove Python bytecode caches and pytest artifacts
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	rm -rf .pytest_cache

distclean: clean ## `clean` + remove the virtualenv (.venv)
	rm -rf .venv
