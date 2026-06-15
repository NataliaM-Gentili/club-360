# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Club 360 is a club/gym management system: clients book recurring time slots ("turnos") for classes ("clases"), pay via card or cash, get waitlisted ("lista de espera") when full, and check in via QR codes. Admins/employees manage classes, payments, and waitlists.

- **Backend**: Flask + Flask-SQLAlchemy (SQLite), Flask-Login/session-based auth, Flask-Mail, qrcode
- **Frontend**: React 19 + Vite + react-router-dom v7, axios, react-toastify, FullCalendar

All domain naming (models, routes, variables, comments) is in **Spanish** — follow this convention for new code.

## Common commands

**Backend** (from `backend/`):
```
python -m venv venv
venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
python run.py                  # runs on http://localhost:8080 (debug=True)
```

**Frontend** (from `frontend/`):
```
npm install
npm run dev       # http://localhost:5173
npm run lint      # eslint
npm run build     # vite build
npm run preview
```

There are no automated test suites in this repo currently.

**Local DB**: SQLite at `backend/instance/database.db` (gitignored — each dev has their own). Tables are created automatically by `db.create_all()` on app startup (see `backend/app/models/db_structure.py`), which also seeds `Rol` and `TipoLista` rows via a SQLAlchemy `after_create` event. Sample-data scripts live in `backend/instance/load_scripts/` (e.g. `setup_datos_prueba.py`, `agregar_turnos_prueba.py`, `crear_usuario_prueba.py`, `clear_db.py`) — run these with `python <script>` from `backend/` against the local `database.db` to get realistic test data.

## Architecture

### Backend (`backend/app/`)

- **`app/models/db_structure.py`**: the single source of truth for all SQLAlchemy table/model classes (`Usuario`, `Cliente`, `Empleado`, `Administrador`, `Clase`, `Turno`, `Reserva`, `ReservaTurno`, `ReservaClase`, `Abono`, `AbonoTarjeta`, `Tarjeta`, `ListaEspera`, `OfrecimientoReserva`, etc.). Add new tables/columns here.
- **`app/models/<entity>_model.py`** (e.g. `user_model.py`, `turno_model.py`, `reserva_model.py`, `clase_model.py`, `tarjeta_model.py`, `lista_espera_models.py`, `asistencia_qr_model.py`, `actividad_model.py`): each defines a `<Entity>Model` class with `@staticmethod` query/business methods that operate on the `db_structure` classes. **Reusable queries go here.**
- **`app/routes/<entity>_routes.py`**: each defines a Flask `Blueprint` (e.g. `user_bp`, `turno_bp`, `clase_bp`, `reserva_bp`, `tarjeta_bp`, `actividad_bp`, `lista_espera_bp`, `asistencia_bp`) with the actual endpoint logic/algorithms, calling into the `*_model` classes. **Logic and algorithms go here.**
- **`app/services/email_services.py`**: sends transactional emails (password reset, QR check-in receipts, waitlist alerts, cancellation notices) via Flask-Mail, and generates QR codes (`qrcode`) as PNG bytes for email attachments.
- **`app/__init__.py`** (`create_app`): initializes `db`, `mail`, CORS (allowing `http://localhost:5173` with credentials), runs `db.create_all()`, and registers every blueprint **without a URL prefix** — e.g. `user_bp` exposes `/login`, `/signup`; `turno_bp` exposes `/visualizar_turnos`, `/buscar_turnos`, etc. directly at the app root.
  - Note: `app/routes/central_routing.py` defines an `all_routes()` helper that registers blueprints under `/api/...`, but it is **not called** from `create_app()` — it's dead code. Don't be misled by it.
- Auth is session-cookie based (`Flask-Login` + Flask `session`); roles are `cliente` (1), `Administrador` (2), `Empleado` (3) via `Usuario.rol_id` → `Rol`.

### Frontend (`frontend/src/`)

- **`main.jsx`** (do not modify per repo convention) wraps the app in `AuthProvider` and renders `AppRoutes`, plus a global `react-toastify` `ToastContainer`.
- **`routes/AppRoutes.jsx`**: all routes in one place. Public routes (`/signup`, `/login`, `/reset-password`, `/olvide-contrasena`) render directly; everything else is nested under `ProtectedLayout` (adds `HeaderNavBar` + `Outlet`).
- **`hooks/AuthContext.jsx`**: `AuthProvider`/`useAuth()` fetch `/api/auth/status` on mount to populate `{ loggedIn, user_id, rol_id }` and `loading`.
- **`pages/`**: one file per page/screen (monolithic page components). **`components/`**: shared reusable pieces (e.g. `HeaderNavBar`, `ModalDialog`, `PaymentModal`, `CardItem`, `EmailVisualization`). **`assets/styles/`**: one CSS file per page/component, **`assets/images/`**: static images.
- **API calls**: the frontend calls `/api/...`; Vite's dev server proxy (`vite.config.js`) strips the `/api` prefix and forwards to `http://localhost:8080` (the Flask backend). So a frontend call to `/api/login` hits the Flask route `/login`.
- `index.html` and `main.jsx` are marked "NO TOCAR" (do not touch) in the original README — avoid editing these unless necessary.

### Cross-cutting domain concepts

- **Clase**: a recurring weekly class (day + time + discipline + cupo/capacity).
- **Turno**: a specific date instance of a `Clase`.
- **Reserva**: a client's booking, linked to either a `Turno` (single session) or a `Clase` (monthly subscription, via `ReservaTurno`/`ReservaClase`).
- **Abono**: payment record for a `Reserva` (cash or card via `AbonoTarjeta`).
- **ListaEspera** / **OfrecimientoReserva**: waitlist entries and the offers sent to waitlisted clients when a spot opens up.
- QR check-in: each reservation's confirmation email includes a QR encoding `id_cliente|id_turno|id_reserva`, scanned at `asistencia_bp`'s `/asistencia/registrar` endpoint.
