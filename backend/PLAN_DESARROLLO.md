# Plan de Desarrollo Detallado - Sistema de Agendamiento y Renta

**Objetivo:** Desarrollar el backend completo (MVP) basado en el `PRD_agendamiento.md` en un plazo de **4 días**.
**Stack:** Python (FastAPI), PostgreSQL, Redis, Docker.
**Frontend (Referencia):** Flutter (se generará cliente OpenAPI).

---

## Cronograma General

| Día | Foco Principal | Entregables Clave |
| :--- | :--- | :--- |
| **Día 1** | **Cimientos y Activos** | Configuración, Auth, CRUD Máquinas, Calendario Base. |
| **Día 2** | **Motor de Subastas** | Lógica de Ofertas, Soft Close, Proxy Bidding, Notificaciones. (COMPLETADO) |
| **Día 3** | **Operaciones y Reservas** | Conversión Oferta->Booking, Fotos, Combustible, Métricas. |
| **Día 4** | **Seguridad y Calidad** | Hardening, Rate Limiting, Tests, Documentación Final. |

---

## Desglose Diario de Actividades

### DÍA 1: Arquitectura, Autenticación y Gestión de Máquinas

**Objetivo:** Tener el sistema base corriendo, usuarios autenticados y el inventario de máquinas con su disponibilidad básica lista.

#### Mañana (08:00 - 12:00) - Configuración y Auth
1.  **Inicialización del Proyecto:**
    *   Estructura de carpetas FastAPI (`app/core`, `app/api`, `app/db`, `app/models`).
    *   Configuración de Docker Compose (App + Postgres + Redis).
    *   Configuración de Alembic para migraciones.
2.  **Módulo de Usuarios (Auth):**
    *   Modelo DB `User`: email, password_hash, role (admin/client/operator), phone.
    *   Implementar JWT (Access + Refresh Tokens).
    *   Endpoints:
        *   `POST /auth/register`
        *   `POST /auth/login`
        *   `POST /auth/refresh`
    *   Middleware de autenticación y permisos (RBAC).

#### Tarde (13:00 - 17:00) - Máquinas y Disponibilidad
3.  **Módulo de Máquinas:**
    *   Modelo DB `Machine`: specs (JSON), location (lat/lng), fuel_type, precios, fotos.
    *   Endpoints CRUD (Admin): `GET`, `POST`, `PUT`, `DELETE` `/machines`.
    *   Filtros de búsqueda: Por proximidad (haversine simple o PostGIS) y tags.
4.  **Módulo de Calendario (Slots):**
    *   Modelo DB `AvailabilitySlot`: machine_id, date, hour_start, status.
    *   **Scheduler V1:** Script (tarea background) que genera slots vacíos para `hoy + 3 días`.
    *   Endpoint: `GET /machines/{id}/calendar` (vista de disponibilidad).

---

### DÍA 2: Motor de Subastas (Bidding) y Notificaciones

**Objetivo:** Implementar la lógica compleja de negocio: subastas, reglas de tiempo y comunicación con el usuario.

#### Mañana (08:00 - 12:00) - Lógica de Ofertas
1.  **Modelo de Ofertas:**
    *   Modelo DB `Offer`: amount, max_bid (proxy), status, expires_at.
    *   Validaciones: No ofertar en slots pasados, oferta > precio base.
2.  **Motor de Subastas (Core):**
    *   **Soft Close:** Lógica que extiende `expires_at` si entra oferta en los últimos X minutos.
    *   **Proxy Bidding:** Algoritmo que calcula automáticamente la oferta ganadora basada en el `max_bid` del usuario.
    *   Endpoint: `POST /offers` (Crear oferta).
    *   Endpoint: `GET /offers` (Ver historial y estado).

#### Tarde (13:00 - 17:00) - Intereses y Notificaciones
3.  **Watchlist:**
    *   Modelo DB `Watchlist`: user_id, machine_id.
    *   Endpoint: `POST /watchlist/toggle`.
4.  **Sistema de Notificaciones:**
    *   Modelo DB `Notification`: user_id, type, payload, read_status.
    *   **Event Triggers:**
        *   Al ser superado (Outbid).
        *   Al ganar una subasta.
        *   Al abrirse disponibilidad (Watchlist).
    *   Simulación de envío (Mock Service) para Email/Push.

---

### DÍA 3: Operaciones, Reservas y Métricas

**Objetivo:** Cerrar el ciclo de negocio (ganar -> reservar -> pagar -> operar) y proveer visión al administrador.

#### Mañana (08:00 - 12:00) - Reservas y Operaciones de Campo
1.  **Gestión de Bookings:**
    *   Modelo DB `Booking`: start/end time, status (pending_payment, confirmed, active, completed).
    *   **Task Background:** Worker que procesa subastas cerradas -> Crea Booking -> Notifica ganador.
2.  **Operaciones (Check-in/Check-out):**
    *   Campos en Booking: `start_photos`, `end_photos`, `start_fuel`, `end_fuel`.
    *   Endpoints para subir evidencia (URLs de fotos).
    *   Lógica de "Call-Off" (Endpoint `POST /bookings/{id}/finish`).

#### Tarde (13:00 - 17:00) - Pagos y Dashboard Admin
3.  **Integración de Pagos (Mock):**
    *   Modelo `Transaction`.
    *   Flujo: Intent de pago al ganar -> Captura al finalizar.
    *   Cálculo de costos extra (combustible, entrega).
4.  **Métricas y Reportes:**
    *   Consultas SQL optimizadas para:
        *   Utilización Financiera (Revenue / Potential).
        *   Horas totales alquiladas.
        *   M3 bombeados (Modelo `PumpMetric`).
    *   Endpoints: `/admin/metrics/machines` y `/admin/metrics/financial`.

---

### DÍA 4: Seguridad, Testing y Entrega

**Objetivo:** Blindar la aplicación, asegurar calidad y preparar documentación para el equipo frontend.

#### Mañana (08:00 - 12:00) - Seguridad (Cybersecurity Hardening)
1.  **Protección de API:**
    *   Implementar **Rate Limiting** (Redis) en endpoints de Auth y Bidding.
    *   Configurar **CORS** restrictivo.
    *   Headers de seguridad (Helmet/Secure Headers).
2.  **Validación y Privacidad:**
    *   Revisión de Pydantic Schemas (Input Validation estricto).
    *   Asegurar que no se expongan datos sensibles en respuestas JSON (User passwords, PII innecesario).

#### Tarde (13:00 - 17:00) - QA y Documentación
3.  **Testing:**
    *   Unit Tests: Reglas de subasta (Proxy bidding, Soft close).
    *   Integration Tests: Flujo completo (User -> Offer -> Booking).
4.  **Finalización:**
    *   Revisión de `openapi.json` (Nombres de operaciones claros para cliente Dart).
    *   Script de **Seeding**: Datos iniciales de máquinas y usuarios para pruebas inmediatas.
    *   Revisión final contra `PRD_agendamiento.md`.

---

## Criterios de Éxito del Plan

1.  **API Funcional:** Todos los endpoints críticos responden correctamente.
2.  **Subasta Real:** El sistema maneja ofertas concurrentes y resuelve ganadores correctamente.
3.  **Seguro:** Rate limiting y Auth robusta implementados.
4.  **Documentado:** Swagger UI accesible y claro.
