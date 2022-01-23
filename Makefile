FILES=$(shell find trainspotting tests -name "*.py")

lint:
	python -m isort trainspotting/ tests/ --check-only && \
	python -m black trainspotting/ tests/ --check --diff && \
	python -m unify --check-only $(FILES) && \
	python -m flake8 trainspotting/ tests/ && \
	python -m mypy trainspotting/ tests/

amaze:
	python -m isort trainspotting/ tests/ && \
	python -m add_trailing_comma $(FILES) && \
	python -m black trainspotting/ tests/ && \
	python -m add_trailing_comma $(FILES) && \
	python -m unify -i $(FILES)