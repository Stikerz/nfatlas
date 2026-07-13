.PHONY: help setup dev test lint typecheck demo-reset clean

help:
	@echo "Atlas V0.5 — dev commands"
	@echo ""
	@echo "  make setup         Copy .env.example, install pnpm lockfile"
	@echo "  make dev           docker compose up (all 5 services)"
	@echo "  make test          Run backend + admin unit tests"
	@echo "  make lint          Ruff + ESLint + Flutter analyze"
	@echo "  make typecheck     mypy + tsc"
	@echo "  make demo-reset    Wipe DB volume and reseed identity slice"
	@echo "  make clean         Stop stack, remove volumes"

setup:
	@if [ ! -f .env ]; then cp .env.example .env; echo "→ created .env from .env.example"; fi
	@cd admin && corepack enable && pnpm install --frozen-lockfile || (echo "→ no lockfile yet; running pnpm install"; cd admin && pnpm install)

dev:
	docker compose up --build

test:
	docker compose run --rm backend pytest -ra
	cd admin && pnpm test

lint:
	docker compose run --rm backend ruff check src tests
	cd admin && pnpm lint
	cd mobile && flutter analyze

typecheck:
	docker compose run --rm backend mypy src
	cd admin && pnpm typecheck

demo-reset:
	docker compose down -v
	docker compose up -d postgres redis mailhog
	@echo "→ waiting for postgres to become healthy…"
	@until docker compose exec -T postgres pg_isready -U atlas -d atlas >/dev/null 2>&1; do sleep 1; done
	docker compose run --rm backend alembic -c migrations/alembic.ini upgrade head
	@echo "→ demo-reset done (identity slice migrations applied)"

clean:
	docker compose down -v
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache
	rm -rf admin/.next admin/node_modules
	rm -rf mobile/.dart_tool mobile/build
