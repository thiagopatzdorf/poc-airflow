.PHONY: bootstrap init up down status logs test lint security-check demo

bootstrap:
	./scripts/bootstrap-secrets.sh

init:
	docker compose run --rm airflow-init

up:
	docker compose up -d --build postgres api-server scheduler dag-processor triggerer

down:
	docker compose down

status:
	docker compose ps
	./scripts/healthcheck.sh

logs:
	docker compose logs --tail=200

test:
	python3 -m pytest -q

lint:
	python3 -m compileall -q dags poc tests

security-check:
	./scripts/security-check.sh

demo:
	./scripts/demo.sh

