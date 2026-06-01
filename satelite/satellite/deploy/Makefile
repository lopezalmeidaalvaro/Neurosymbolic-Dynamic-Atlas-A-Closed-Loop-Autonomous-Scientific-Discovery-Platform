# Autonomous Spacecraft Thermal OS - Deployment Makefile

.PHONY: up down logs reset status

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

reset:
	docker compose down -v
	docker compose up -d --build

status:
	docker compose ps
