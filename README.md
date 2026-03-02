# AMS — Správa montáží

Interní systém pro správu montážních zakázek. Backend Django + DRF, frontend React + TypeScript.

## Architektura

```
Django 5.2 + DRF 3.16    →  REST API   (/api/v1/)
React 19  + Vite 7       →  SPA        (frontend/)
JWT httpOnly cookies      →  Autentizace
SQLite / PostgreSQL       →  Databáze
```

## Požadavky

- Python 3.12+
- Node.js 20+

## Instalace

```bash
# Backend
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux
pip install -r requirements.txt
cp .env.example .env          # upravte hodnoty
python manage.py migrate
python manage.py createsuperuser

# Frontend
cd frontend
npm install
```

## Spuštění (dev)

```bash
# Terminal 1 — Backend
python manage.py runserver

# Terminal 2 — Frontend (Vite proxy → localhost:8000)
cd frontend
npm run dev
```

Aplikace běží na `http://localhost:5173`, API na `http://localhost:8000/api/v1/`.

## Struktura

```
AMS/              Django projekt (settings, urls)
api_v1/           DRF ViewSets, serializers, filtry
app_sprava_montazi/
  models.py       Datový model (Order, Client, Team, …)
  OOP_*.py        Business logika (protokoly, emaily, dashboard)
  management/     Django management commands
accounts/         Uživatelský model
frontend/
  src/
    api/          Axios klient + endpointy
    features/     Stránky (orders, clients, teams, dashboard, …)
    components/   Sdílené komponenty (Toast, Layout, …)
    types/        TypeScript typy
configs/          Nginx, systemd, fail2ban konfigurace
bot.py            Selenium bot (běží samostatně)
```

## API endpointy

- `GET /api/v1/orders/` — seznam zakázek (filtrování, řazení, stránkování)
- `GET /api/v1/clients/` — seznam zákazníků
- `GET /api/v1/teams/` — týmy
- `GET /api/v1/dashboard/` — statistiky
- `GET /api/v1/distrib-hubs/` — distribuční huby
- `POST /api/v1/auth/login/` — přihlášení (JWT cookies)
- `GET /api/schema/swagger-ui/` — Swagger dokumentace

## Licence

Interní projekt — neveřejné.
