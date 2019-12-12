lint:
	flake8 . --max-complexity=10 --max-line-length=127 --exclude=venv

run_tests:
	pytest test/