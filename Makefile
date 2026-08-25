.PHONY: help setup dev test lint typecheck demo-reset demo-seed demo-close-reveal bootstrap clean

help:
	@echo "Atlas V0.5 — dev commands"
	@echo ""
	@echo "  make setup         Copy .env.example, install pnpm lockfile"
	@echo "  make dev           docker compose up (all 5 services)"
	@echo "  make test          Run backend + admin unit tests"
	@echo "  make lint          Ruff + ESLint + Flutter analyze"
	@echo "  make typecheck     mypy + tsc"
	@echo "  make demo-reset    Wipe DB volume and reseed identity slice"
	@echo "  make demo-seed     Populate one active draw + 10 skill questions"
	@echo "  make demo-close-reveal  Close + reveal the seeded draw for the demo pitch"
	@echo "  make bootstrap     Create the seeded superadmin (Adaobi Ibe)"
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
	@echo "→ full demo reset: wipe volume + migrate + seed + bootstrap"
	@START=$$(date +%s); \
	docker compose down -v >/dev/null 2>&1; \
	docker compose up -d postgres redis mailhog >/dev/null 2>&1; \
	echo "→ waiting for postgres to become healthy…"; \
	until docker compose exec -T postgres pg_isready -U atlas -d atlas >/dev/null 2>&1; do sleep 1; done; \
	docker compose run --rm backend alembic -c migrations/alembic.ini upgrade head; \
	docker compose run --rm backend python /infrastructure/scripts/seed_v0_5.py; \
	docker compose run --rm backend python /infrastructure/scripts/bootstrap_superadmin.py; \
	docker compose up -d >/dev/null 2>&1; \
	END=$$(date +%s); \
	echo "→ demo-reset done in $$((END - START))s (target: < 30s)"; \
	printf '→ waiting for backend to become healthy…'; \
	until curl -sf http://localhost:8000/healthz >/dev/null 2>&1; do printf '.'; sleep 2; done; \
	echo ' ready'; \
	echo "→ stack is up — backend :8000, mailhog :8025; admin :3000 still compiling (~45s)"

demo-seed:
	docker compose run --rm backend python /infrastructure/scripts/seed_v0_5.py

demo-close-reveal:
	@echo "→ closing + revealing the seeded demo draw"
	docker compose run --rm backend python /infrastructure/scripts/demo_close_reveal.py

bootstrap:
	docker compose run --rm backend python /infrastructure/scripts/bootstrap_superadmin.py

clean:
	docker compose down -v
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache
	rm -rf admin/.next admin/node_modules
	rm -rf mobile/.dart_tool mobile/build
