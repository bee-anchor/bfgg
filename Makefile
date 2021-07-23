.PHONY: bfgg-up, bfgg-down

lint:
	black .

run_tests:
	pytest test/

bfgg-up:
	docker-compose build
	docker-compose up -d localstack
	python scripts/setup_localstack.py
	docker-compose up -d controller agent gui

bfgg-down:
	docker-compose down