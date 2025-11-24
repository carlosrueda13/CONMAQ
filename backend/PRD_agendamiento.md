# PRD - Sistema de Agendamiento y Renta de Equipos

**Versión:** 0.1

**Autor:** Equipo Backend

**Fecha:** 2025-11-24

---

**Resumen ejecutivo**

Desarrollar un backend completo para una plataforma de agendamiento y renta por horas de equipos (ej. bombas, maquinaria). Usuarios registrados pueden ver equipos, su calendario de disponibilidad y ofertar por horarios. Cuando varios usuarios compiten por la misma máquina en el mismo slot horario, se permite un mecanismo de oferta (bidding). El sistema debe soportar roles (cliente, administrador, operador), notificaciones a usuarios interesados, integración con servicios externos (mapas/distancia, pago, email/SMS), y métricas administrativas (horas alquiladas, precio promedio, m3 bombeados, distancias, etc.).

Objetivo principal: construir un backend escalable, seguro y mantenible que implemente la lógica de disponibilidad, subasta de slots y generación de métricas operativas.

---

**Alcance**

- Backend REST/GraphQL con autenticación y autorización.
- API pública para clientes (navegación, ver disponibilidad, ofertar, reservar, ver historial).
- API administrativa para métricas y gestión de máquinas, tarifas y horarios.
- Integración con: base de datos relacional (PostgreSQL), sistema de colas (Redis + Celery/RQ), servicio de notificaciones (Push/Email/SMS), proveedor de mapas (Google Maps/Mapbox), gateway de pagos (Stripe u otro), y opcional telemetría/IoT para lectura de m3 bombeados.
- Sistema de ofertas/bidding para slots con reglas configurables.
- Scheduler que habilite los horarios con 3 días de anticipación.

---

**Supuestos y restricciones**

- El mínimo tiempo de renta por máquina se configurará por máquina (por ejemplo, 1 hora, 2 horas).
- Precio base por hora se define por máquina; los usuarios pueden ofertar por debajo o encima del precio base.
- El sistema de ofertas se resuelve automáticamente tras un periodo configurable (por ejemplo, 15 minutos tras la primera oferta para ese slot) o mediante reglas (p. ej., la oferta más alta al cierre).
- Las reservas bloquean disponibilidad y pueden requerir retención de pago (autorización de tarjeta) hasta que se complete o cancele.

---

**Roles y permisos**

- Cliente: registrarse/login, ver catálogo, marcar interés en máquinas, ver disponibilidad, ofertar por slots, pagar, ver historial y notificaciones.
- Administrador: CRUD de máquinas, gestionar tarifas, ver métricas (horas alquiladas, precios promedio, m3, distancias), gestionar usuarios y conflictos, exportar reportes.
- Operador/Transportista (opcional): ver asignaciones de envío, detalles de ubicación y distancia, marcar inicio/fin de servicio, reportar m3 bombeados.

---

**Requerimientos funcionales (detallados)**

1) Autenticación y autorización
- Registro y login con email+password.
- JWT (Access + Refresh tokens) o OAuth2 (opcional SSO) con roles.
- Endpoints: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `POST /auth/forgot-password`.

2) Gestión de máquinas
- CRUD de máquinas (admin): `GET/POST/PUT/DELETE /machines`.
- Datos por máquina: id, nombre, descripción, especificaciones técnicas (potencia, caudal m3/h, peso, consumo), precio_base_por_hora, minimo_horas, ubicación (lat,lng, dirección), fotos, estado (activo/inactivo/mantenimiento), capacidades (m3_max_hora), tags.
- Buscar máquinas por proximidad, tags, disponibilidad.

3) Calendario y disponibilidad
- Representar disponibilidad por slots horarios de 1 hora (configurable granuralidad).
- Un slot se identifica por `machine_id`, `date` (YYYY-MM-DD), `hour_start` (0..23), `duration_hours`.
- Reglas:
  - Un día se habilita 3 días antes (ej. miércoles activado el domingo). Implementar scheduler que active/crea slots disponibles cuando corresponde.
  - Min rental duration: al reservar, el usuario debe pedir al menos `minimo_horas` de la máquina.
  - Evitar solapamientos: no permitir reservas que colisionen con bookings confirmadas.

4) Ofertas / Bidding
- Cuando múltiples usuarios quieren el mismo `machine_id` y slot, pueden colocar ofertas por el slot.
- Modelo de oferta:
  - `Offer`: id, user_id, machine_id, date, hour_start, offered_price_total (o por hora), quantity_hours, status (active, outbid, won, lost, cancelled), created_at, expires_at, `max_bid_amount` (para proxy bidding).
  - Reglas de subasta:
    - **Ventana de subasta:** Configurable (ej. 15-30 min).
    - **Soft Close (Popcorn Bidding):** Si entra una oferta en los últimos X minutos (ej. 2 min), el tiempo de cierre se extiende automáticamente para evitar "sniping".
    - **Proxy Bidding:** El usuario define un monto máximo y el sistema oferta automáticamente el incremento mínimo necesario para mantenerlo como ganador hasta su tope.
    - **Precio de Reserva:** El dueño puede definir un precio mínimo oculto; si no se alcanza, la subasta puede declararse desierta o requerir aprobación manual.
  - Notificar a usuarios con `interest` o cercanos por ubicación (filtro) cuando se crea una oferta.

5) Watchlist / Intereses y notificaciones
- Usuarios pueden marcar máquinas como `interested` y recibir notificaciones de nuevas ofertas o cambios de disponibilidad.
- Notificaciones críticas:
  - "Te han superado en la oferta" (con botón de puja rápida).
  - "Renta finaliza en 1 hora" (opción de extender o finalizar).
  - "Operador en camino" (tracking estilo Uber).
- Canales: correo, push (web/mobile), SMS (opcional).

6) Reservas, Operaciones y Pagos
- **Check-in / Check-out con Fotos:** Obligatorio subir 4 fotos (lados) + foto de medidor de combustible/horas al inicio y fin para gestionar disputas (inspirado en Turo).
- **Combustible y Mantenimiento:** Registro de nivel de combustible al inicio y fin. Cargo automático si se devuelve con menos combustible.
- **Seguros:** Campo para gestionar `insurance_status` (Waiver comprado vs. Certificado de Seguro COI validado).
- **Call-Off / Extensión:** El usuario debe marcar "Fin de renta" (Call-Off). Si no lo hace, la facturación continúa o se aplican penalidades.
- **Costos de Movilización:** Calcular tarifa de envío dinámica basada en distancia antes de la oferta (Total Landed Cost).
- Integración con pasarela de pagos (Stripe recomendado): retener tarjeta (authorise) y capturar al finalizar.

7) Métricas y reporting (admin)
- **Utilización Financiera (%):** Ingresos reales vs. Ingresos potenciales (Standard Rate).
- **ROI por Máquina:** Ingresos acumulados vs. (Costo Adquisición + Costo Mantenimiento).
- **Salud de Flota:** Alertas de mantenimiento basadas en `engine_hours` (ej. servicio cada 500h).
- Horas totales alquiladas por máquina (y por período).
- Precio promedio por hora por máquina y por tipo/region.
- Horarios más demandados (por hora y día de la semana).
- Usuario actual que tiene alquilada la máquina y duración restante.
- Ubicación destino para la máquina y distancia desde base (calcular via Maps API).
- m3 bombeados por booking (sum per booking), m3 totales bombeados por máquina.
- Exportar CSV/PDF y endpoints para dashboard.

8) Telemetría / m3 pumped
- Soporte para ingresar m3 bombeados manualmente por operador o mediante integración IoT/webhook que registre lecturas.
- Modelo: `PumpMetric` con booking_id, machine_id, timestamp, m3_delta, cumulative_m3.

9) Integraciones externas
- Map provider: Google Maps / Mapbox para cálculo de distancia y ETA (server-side requests).
- Payments: Stripe (o similar) para authorizations, captures y reembolsos.
- Email: SendGrid, Mailgun, o proveedor SMTP.
- SMS: Twilio (opcional).
- Notifications push: FCM / APNs para mobile; Web Push para web.

10) Scheduler y tareas background
- Scheduler para activar slots 3 días antes (cron job diario a 00:00 UTC o similar).
- Tasks: resolver subastas al cierre, enviar notificaciones, reconciliar pagos, procesar métricas, limpiar ofertas expiradas.
- Colas: Redis + worker (Celery, RQ o BullMQ dependiendo del stack).

11) API pública y contratos
- Documentar con OpenAPI/Swagger.
- Versionado de API: `/api/v1/...`.

---

**Requerimientos no funcionales**

- Escalabilidad: servicios stateless, PostgreSQL para datos, Redis para cache y colas.
- Disponibilidad: deploy en Kubernetes o PaaS con auto-scaling.
- Seguridad: HTTPS, cifrado de datos sensibles, OWASP best-practices, rate-limiting, logs de auditoría.
- Observabilidad: tracing (OpenTelemetry), métricas Prometheus, alerting.
- SLA: 99.9% para endpoints críticos.

---

**Modelo de datos (esquema simplificado)**

- `users` (id, email, password_hash, name, role, phone, created_at, last_login, location_lat, location_lng, preferences)
- `machines` (id, name, description, specs JSON, price_base_per_hour, min_hours, location_lat, location_lng, address, capacity_m3h, photos[], status, created_at, `fuel_type`, `tank_capacity`, `current_engine_hours`, `service_interval_hours`, `acquisition_cost`, `maintenance_cost_total`)
- `availability_slots` (id, machine_id, date, hour_start, hour_end, is_active, created_at, `reserve_price`)
- `offers` (id, user_id, machine_id, date, hour_start, hours, price_per_hour, total_price, status, expires_at, created_at, `max_bid_amount`, `is_proxy_active`)
- `bookings` (id, user_id, machine_id, start_datetime, end_datetime, total_price, status, payment_status, created_at, `insurance_type` (waiver/coi), `start_fuel_level`, `end_fuel_level`, `start_photos[]`, `end_photos[]`, `delivery_fee`, `actual_return_datetime`)
- `watchlists` (id, user_id, machine_id, created_at)
- `notifications` (id, user_id, type, payload JSON, delivered, read, created_at)
- `pump_metrics` (id, booking_id, machine_id, timestamp, m3_delta, cumulative_m3)
- `locations` (id, machine_id, lat, lng, address) -- optional separate table
- `transactions` (id, booking_id, provider, provider_id, amount, currency, status, created_at)

Indices importantes: index on `machine_id,date,hour_start` (availability/offers), geospatial index on `location_lat,location_lng`.

---

**Endpoints propuestos (resumen)**

- Auth
  - POST `/api/v1/auth/register`
  - POST `/api/v1/auth/login`
  - POST `/api/v1/auth/refresh`

- Machines
  - GET `/api/v1/machines` (filtros: lat,lng,radius,tags,available_from,available_to)
  - GET `/api/v1/machines/:id`
  - POST `/api/v1/machines` (admin)
  - PUT `/api/v1/machines/:id` (admin)

- Availability & Calendar
  - GET `/api/v1/machines/:id/calendar?start=YYYY-MM-DD&end=YYYY-MM-DD`
  - GET `/api/v1/machines/:id/slots?date=YYYY-MM-DD`

- Offers / Bidding
  - POST `/api/v1/offers` (crear oferta)
  - GET `/api/v1/offers?user_id=&machine_id=`
  - GET `/api/v1/offers/:id`

- Bookings
  - POST `/api/v1/bookings` (crear booking directo o resultado de oferta ganadora)
  - GET `/api/v1/bookings` (user/admin views)
  - POST `/api/v1/bookings/:id/cancel`

- Watchlist / Interest
  - POST `/api/v1/watchlist` (toggle)
  - GET `/api/v1/watchlist`

- Admin metrics
  - GET `/api/v1/admin/machines/:id/metrics?from=&to=`
  - GET `/api/v1/admin/reports/usage?from=&to=`

- Notifications
  - GET `/api/v1/notifications`
  - POST `/api/v1/notifications/:id/ack`

---

**Reglas de negocio destacadas**

- Activación de slots: ejecutor diario que crea/activa slots para `today + 3 days`.
- Si una oferta gana, el sistema creará un `booking` y bloqueará el slot; se retendrá pago si aplica.
- Ofertas simultáneas en el mismo slot: orden por `price` y `created_at`. Soporte para outbidding.
- Reserva mínima y máxima controladas por `machines.min_hours` y una política global opcional.
- Llegada tardía / no-show: política configurable con penalizaciones.

---

**Integraciones externas y consideraciones operativas**

- Maps & Distance: usar Google Maps Distance Matrix API o Mapbox Directions Matrix para calcular distancias y tiempos. Guardar estimaciones en `bookings` para el operador.
- Pagos: Stripe recommended — usar PaymentIntent para retener y confirmar pagos.
- Emails: SendGrid para transacciones y notificaciones.
- SMS: Twilio para alertas críticas.
- IoT/telemetría: endpoints webhook `POST /api/v1/telemetry` para ingestión de m3 (sensible a autenticación por token).

---

**Seguridad y privacidad**

- Almacenar contraseñas con bcrypt/argon2.
- Guardar tokens de terceros de forma cifrada en la DB.
- Logs de auditoría para acciones sensibles (cancelaciones, cambios de precio, transferencias de bookings).
- Cumplimiento con normativa local de protección de datos (p. ej. GDPR si aplica). Añadir consentimiento de uso de datos.

---

**Escenario de flujo principal (usuario reserva vía oferta)**

1. Usuario A consulta calendario de `machine X` para `2025-12-01 10:00`.
2. Usuario A crea `Offer` por ese slot por un total $100.
3. Se abre ventana de bidding (configurable) y usuarios marcados como `interested` o cercanos reciben notificación.
4. Usuario B y C crean ofertas superiores.
5. Al cierre de la ventana, la oferta más alta (B) gana; el sistema crea una `Booking` en estado `pending_payment` y envía request para autorizar la tarjeta del ganador.
6. Si el pago se autoriza, booking cambia a `confirmed` y slot queda ocupado; si falla, siguiente oferta más alta se evalúa.

---

**Casos de borde y consideraciones**

- Conflictos de solapamiento por multi-hora: validar solapamientos por todo el rango horario solicitado.
- Cancelaciones y reembolsos: política con tiempos límite (p. ej. cancelación gratuita hasta 24h antes).
- Oferta fraudulenta: límites por usuario y detección de patrones (rate-limits, verificación KYC para altas cantidades).
- Disputa entre usuarios: endpoint y flujo para que admin revise y reasigne/manualmente resuelva.

---

**Diseño técnico y stack recomendado**

- Lenguaje/Framework: Python + FastAPI (rápido para APIs), o Node.js + NestJS si el equipo prefiere TypeScript.
- DB: PostgreSQL (relacional para transacciones y consultas analíticas simples) + PostGIS si se necesita geospatial avanzado.
- Cache/Queue: Redis para caching y cola (RQ/Celery/BullMQ según stack).
- Workers: Celery (Python) o BullMQ (Node) para procesar subastas, notificaciones y tareas programadas.
- Migrations: Alembic (Python) o TypeORM migrations.
- Tests: pytest or jest, cobertura mínima de 70% para lógica crítica (booking, ofertas, pagos).
- Contenerización: Docker + docker-compose para dev; Kubernetes para producción.
- CI/CD: GitHub Actions con lint, tests, build, deploy.

---

**Plan mínimo viable (MVP) - entregables**

Fase 0 - Planificación (esta PRD) - Aprobado.

Fase 1 - Core API (2-3 semanas)
- Auth JWT, Users endpoints.
- Machines CRUD + catálogo básico.
- Calendar/slots model y scheduler que activa slots a +3 días.
- Crear ofertas simples y ver ofertas.
- Crear bookings a partir de ofertas ganadoras manualmente (sin integración de pagos aún).

Fase 2 - Subasta y notificaciones (2 semanas)
- Implementar ventana de bidding automática y resolución.
- Notificaciones por Email (SendGrid) y Webhooks para push.
- Watchlist/Interest.

Fase 3 - Pagos y métricas (2 semanas)
- Integración Stripe (authorise & capture).
- Endpoints admin métricas (horas, precios medios, m3 pumped).

Fase 4 - Integraciones avanzadas y operaciones (2-3 semanas)
- Map distance estimates (Google/Mapbox).
- Telemetría IoT (ingestión m3).
- Dashboard admin, exportes y seguridad avanzada.

---

**Criterios de aceptación (MVP)**

- Usuarios pueden registrarse e iniciar sesión.
- Usuarios ven catálogo y calendario de máquinas con slots habilitados hasta 3 días por adelantado.
- Usuarios pueden crear ofertas para un mismo slot y la plataforma notifica a usuarios interesados.
- Subasta se resuelve según la ventana configurada y crea booking al ganador.
- Admin puede ver horas alquiladas y precio promedio por máquina en un periodo dado.

---

**Testing y QA**

- Unit tests para lógica de ofertas, solapamientos y creación de bookings.
- Integration tests con DB (Postgres test container) y mock de Stripe/Maps.
- E2E tests básicos simulando flujo oferta -> booking -> pago.

---

**Observability y Operaciones**

- Logs estructurados (JSON) en stdout.
- Metrics: Prometheus counters (requests, errors, bookings_created, offers_created).
- Tracing: OpenTelemetry.

---

**Siguientes pasos propuestos**

1. Revisar este PRD y aprobar o solicitar cambios.
2. Elegir stack definitivo (FastAPI vs NestJS) y proveedor de pagos.
3. Crear backlog de historias y tasks para Fase 1.

---

**Apéndice — inspiración y requisitos adicionales extraídos de plataformas similares**

- **Sunbelt Rentals / United Rentals / BigRentz:**
  - Protocolo "Call-Off" para finalizar renta.
  - Gestión de seguros (Damage Waiver vs COI).
  - Políticas de combustible (Fuel Level Out/In) y cargos por reabastecimiento.
  - Costos de movilización dinámicos.
  - Métricas de utilización financiera y TCO.

- **Ritchie Bros / IronPlanet (Subastas industriales):**
  - Soft Close (Popcorn Bidding) para evitar sniping.
  - Proxy Bidding (oferta máxima automática).
  - Precios de reserva ocultos.

- **Turo / Airbnb:**
  - Documentación fotográfica obligatoria (Check-in/Check-out) para reducir disputas.
  - Notificaciones en tiempo real ("Driver en camino", "Renta finalizando").

Incluir como features futuras: tarifas dinámicas, rama de operador para asignaciones de transportistas, integración con inventario físico (estado máquina en tiempo real), y reglas de geofencing para restricciones.

---

Fin del documento.
