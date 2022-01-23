lint:
	python -m isort trainspotting/ tests/ --check-only && \
	python -m black trainspotting/ tests/ --check --diff && \
	python -m unify --check-only $(find trainspotting -name "*.py") $(find tests -name "*.py") && \
	python -m flake8 trainspotting/ tests/ && \
	python -m mypy trainspotting/ tests/

amaze:
	python -V && \
	python -m isort trainspotting/ tests/ && \
	python -m add_trailing_comma $(find trainspotting -name "*.py") $(find tests -name "*.py") && \
	python -m black trainspotting/ tests/ && \
	python -m add_trailing_comma $(find trainspotting -name "*.py") $(find tests -name "*.py") && \
	python -m unify -i $(find trainspotting -name "*.py") $(find tests -name "*.py")