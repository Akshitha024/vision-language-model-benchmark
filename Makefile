.PHONY: help install lint typecheck test bench plots clean

PROVIDERS ?= mock
TASKS ?= docvqa,chartqa,mmmu

help:
	@echo "make install / lint / typecheck / test"
	@echo "make bench PROVIDERS=mock TASKS=docvqa,chartqa - run the synthetic bench"
	@echo "make plots - regenerate the 5 chart types"

install: ; uv sync --all-extras
lint:
	uv run ruff check src tests
	uv run ruff format --check src tests
typecheck: ; uv run mypy src
test: ; uv run pytest -m "not slow and not needs_provider"
bench: ; uv run vlm bench --providers $(PROVIDERS) --tasks $(TASKS)
plots: ; uv run vlm plots
clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
