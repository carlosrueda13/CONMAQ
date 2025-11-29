# Informe de Auditoría – Rendimiento y Escalabilidad (Backend CONMAQ)

## 1. Calificación

**Calificación global en “Rendimiento y Escalabilidad”: _6 / 10_**

---

## 2. Explicación de la calificación

### 2.1. Resumen

El backend de CONMAQ tiene una base **correcta y sólida para un MVP**, pero aún no llega al nivel de “buen desempeño bajo alta concurrencia” descrito en la banda 7–9:

- Se usan **FastAPI + Uvicorn** (imagen `python:3.11-slim`, ejecución via `uvicorn app.main:app --reload` en el `Dockerfile` y en `docker-compose.yml`), que por diseño soportan buena concurrencia.
- Se ha integrado **Redis** y hay `celery`, `flower` en `requirements.txt`, lo que indica una intención de usar colas de trabajo y descargar tareas pesadas.
- Hay **rate limiting** (`slowapi`) configurado en `app/main.py` y usado en rutas (`@limiter.limit` en `users.py`), lo cual protege de abusos o DoS básicos.
- La base de datos tiene un diseño **razonablemente optimizado**:
  - Alembic migrations definen índices en columnas clave (`ix_machine_name`, `ix_machine_serial_number`, índices en `availabilityslot`, `user`, `offer`, `watchlist`, `notification`, `booking`, `transaction`).
- Uso de **Alembic** con `env.py` apuntando a `settings.DATABASE_URL` → permite evolucionar el schema manteniendo la performance.

Sin embargo, faltan varias piezas para alcanzar 7–9:

- El despliegue está pensado con **Uvicorn en modo `--reload`**, sin configuración de múltiples workers ni servidor de producción real (Gunicorn + Uvicorn workers).
- No hay evidencia de:
  - Endpoints **async** (`async def`) aprovechando I/O no bloqueante (toda la capa API mostrada está en funciones síncronas).
  - Implementación real de **caché** (aunque Redis está presente en stack y env vars).
  - **Pruebas de carga** (locust, k6, vegeta, wrk) ni ajustes a partir de resultados.
  - Configuración de **workers Celery** en docker-compose (solo se declara `redis`, pero no `worker` ni `beat`).
- El sistema está bien diseñado para escalar **en teoría** (PRD habla de Kubernetes, autoscaling, colas, métricas Prometheus, etc.), pero muchas de esas piezas aún no están operativas en el código/config actual.

Por ello:

- Supera las bandas 2–4, porque:
  - Usa un servidor asíncrono moderno (FastAPI+Uvicorn).
  - Tiene una base de datos con índices.
  - Incorpora rate limiting y Redis en el stack.
- Encaja mejor en **5–6**:

> “Uso de Uvicorn/Gunicorn con múltiples workers (procesos), quizás alguna ruta async. Se aplican optimizaciones puntuales (…) El API funciona bajo carga moderada pero aún puede degradarse en picos altos.”

En el caso concreto:

- Hay **infra para rendimiento medio** (FastAPI, Uvicorn, Redis, Alembic, índices) y protección básica (slowapi).
- Pero falta pasar de **MVP bien armado** a **sistema optimizado y medido**.

**Conclusión:** 6/10 es coherente: base correcta, lista para mejorar; aún no “optimizada y probada” para alto tráfico.

---

### 2.2. Puntos fuertes en rendimiento y escalabilidad

#### 2.2.1. Stack técnico apropiado para alta concurrencia

- **FastAPI** como framework principal (`app/main.py`).
- **Uvicorn** como ASGI server (`CMD ["uvicorn", "app.main:app", ...]` en `backend/Dockerfile`).
- `requirements.txt` incluye:
  - `fastapi`, `uvicorn[standard]`
  - `sqlalchemy`, `alembic`
  - `redis`, `celery`, `flower`
- `docker-compose.yml` levanta:

  ```yaml
  services:
    web:
      build: .
      command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
      ...
    db:
      image: postgres:15-alpine
    redis:
      image: redis:7-alpine
  ```

Esto da una base muy razonable para crecer:

- FastAPI puede manejar muchas conexiones concurrentes si se usa apropiadamente.
- Redis disponible permite caching, rate limiting, colas.
- PostgreSQL bien configurado puede escalar verticalmente y horizontalmente (read replicas) si se necesitara.

#### 2.2.2. Diseño de base de datos con índices relevantes

Alembic migrations:

- `67fca4266a95_initial_migration.py` define índices:

  - `machine`:
    - `ix_machine_id`
    - `ix_machine_name`
  - `user`:
    - `ix_user_email` (unique)
    - `ix_user_full_name`
    - `ix_user_id`
  - `availabilityslot`:
    - `ix_availabilityslot_id`
    - `ix_availabilityslot_start_time`
    - `ix_availabilityslot_end_time`

- `bba41f562bcc_add_serial_number_to_machines.py`:

  - `ix_machine_serial_number` (unique).

- `3db25977c22c_add_offer_model_and_update_.py`:

  - `ix_offer_id`.

- `6d495d6029a4_add_watchlist_and_notification_models.py`:

  - `ix_watchlist_id`
  - `ix_notification_id`.

- `1fb859e04cdb_add_booking_table.py`:

  - `ix_booking_id`.

- `7a25e71a7f05_add_transaction_table.py`:

  - `ix_transaction_id`.

Esto muestra preocupación por:

- Consultas frecuentes sobre IDs y campos clave.
- Integridad referencial (`ForeignKeyConstraint` en offers, bookings, transactions, etc).

Aunque se podrían añadir más índices compuestos (ej. `machine_id + start_time` en `availabilityslot`), la base actual es buena y evita muchos full scans.

#### 2.2.3. Uso de Redis y rate limiting

- `docker-compose.yml` expone Redis:

  ```yaml
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  ```

- `requirements.txt` incluye `redis`, `slowapi`.
- `app/main.py`:

  ```python
  from slowapi import _rate_limit_exceeded_handler
  from slowapi.errors import RateLimitExceeded
  from app.core.limiter import limiter

  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  ```

- `users.py`:

  ```python
  from app.core.limiter import limiter

  @router.post("/", response_model=UserSchema)
  @limiter.limit("5/minute")
  def create_user(...):
      ...
  ```

Esto es muy positivo:

- Ayuda a proteger endpoints sensibles (`/users/`, y potencialmente `/auth/*`, `/offers/*`) contra abuso.
- Reduce riesgo de cuellos de botella por “spikes” repentinos.

#### 2.2.4. Diseño pensando en colas y tareas background

En `PRD_agendamiento.md` y `PLAN_DESARROLLO.md` se especifica:

- Uso de **Redis + Celery** para:
  - Resolver subastas al cierre.
  - Enviar notificaciones.
  - Scheduler para crear slots a `today + 3 days`.
  - Procesar tareas pesadas de pagos, métricas, etc.

`requirements.txt` incluye `celery` y `flower`, confirmando la intención.

Aunque hoy no hay `worker` definido en `docker-compose.yml`, el diseño conceptual ya separa:

- API sincrónica/responsiva.
- Trabajo pesado en background.

Esto es clave para escalabilidad futura.

---

### 2.3. Debilidades y riesgos actuales

#### 2.3.1. Falta de configuración de servidor de producción con múltiples workers

- `backend/Dockerfile` corre:

  ```dockerfile
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  ```

- `docker-compose.yml` hace lo mismo.

Problemas:

- `--reload` es solo para desarrollo; no apto para producción (más overhead, menos estabilidad).
- Sin `--workers` (Gunicorn) ni `--workers` propios de Uvicorn en producción, usas un único proceso Python:

  - Escala en concurrencia I/O-bound, pero no aprovecha múltiples cores para CPU-bound (por ejemplo, hashing de contraseñas, serialización intensa, lógica de subasta si se vuelve compleja).
  - Ante carga alta, un solo proceso se saturará más fácil.

Según la rúbrica, para 7–9 se espera:

- Configuración explícita de workers / clustering en producción.

#### 2.3.2. Ausencia (visible) de endpoints asíncronos (`async def`)

Por los fragmentos vistos (`users.py`, `watchlist.py`, `notifications.py`, `metrics.py`), todas las vistas son:

```python
def read_notifications(...):
    ...

def toggle_watchlist(...):
    ...
```

En FastAPI:

- Esto es **válido** y FastAPI maneja esto bien.
- Pero para aprovechar realmente la asincronía en I/O:

  - Idealmente se exponen endpoints `async def`.
  - Se usan ORMs/Drivers asíncronos (ej. `asyncpg` con SQLAlchemy 2 async, o directamente `databases`/`encode`).

Limitación:

- Toda operación bloqueante (consulta DB síncrona, llamada HTTP sync, etc.) **bloquea el worker** durante su duración.
- En modo single worker, esto reduce el throughput total.

#### 2.3.3. Redis presente, pero sin caché ni workers configurados

- Redis se usa ya para:
  - Rate limiting (`slowapi`, presumiblemente con backend Redis).
- No se ve:
  - Una **capa de caching** para endpoints de lectura intensiva (por ejemplo, catálogo de máquinas, métricas).
  - Definición de `worker` Celery en `docker-compose.yml`.

Impacto:

- Algunas operaciones de lectura (listado de máquinas, métricas) pueden recalcular datos cada vez, presionando la base de datos bajo carga alta.
- Tareas que podrían ir a background (p.ej. envíos de notificaciones, procesamiento de métricas pesadas) pueden estar sucediendo en el request sync.

#### 2.3.4. Falta de pruebas de carga y tuning basado en datos

En el código y documentación:

- `PRD_agendamiento.md` menciona métricas, observabilidad, Prometheus, OpenTelemetry.
- Pero no hay:

  - Scripts de carga (`locustfile.py`, `k6` scripts, etc.).
  - Config de Prometheus/OpenTelemetry en `requirements.txt` o en código.
  - Documentación de resultados de benchmarking.

Esto significa que:

- La arquitectura está bien pensada, pero no hay evidencia de **validación empírica** de cómo responde bajo carga real/esperada.

---

## 3. Plan detallado de mejoras y correcciones  
*(Muy detallado – estilo manual LEGO, paso a paso)*

### 3.1. Objetivos del plan

1. Pasar de **6/10** a **7–8/10** en Rendimiento y Escalabilidad.
2. Hacerlo **incrementalmente**, sin romper el MVP.
3. Preparar el terreno para, más adelante, llegar a un **9–10/10** con:
   - Endpoints críticos asíncronos.
   - Colas de trabajo robustas.
   - Caching y pruebas de carga sistemáticas.

---

### 3.2. Paso 1 – Separar completamente configuración de desarrollo y producción

**Objetivo:** Evitar que la configuración de dev (`--reload`, un solo worker) llegue a producción.

**Pasos:**

1. **Crear dos comandos de ejecución diferentes**

   - En el `Dockerfile`, mantener `CMD` amigable para desarrollo, pero:
     - Añadir documentación sobre cómo iniciar en producción.
   - Ejemplo:

     ```dockerfile
     # Para desarrollo (ya está):
     CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
     ```

   - Añadir en `DOCUMENTACION_TECNICA.md` sección “Despliegue en Producción” una recomendación:

     ```bash
     # Producción usando gunicorn + uvicorn workers
     gunicorn -k uvicorn.workers.UvicornWorker \
       -w 4 \
       -b 0.0.0.0:8000 \
       app.main:app
     ```

2. **Crear un `docker-compose.prod.yml` (opcional)**

   - Con un comando más adecuado:

     ```yaml
     services:
       web:
         build: .
         command: >
           gunicorn -k uvicorn.workers.UvicornWorker
                    -w 4
                    -b 0.0.0.0:8000
                    app.main:app
         environment:
           - UVICORN_HOST=0.0.0.0
           - UVICORN_PORT=8000
         depends_on:
           - db
           - redis
     ```

3. **Documentar claramente**

   - En `DOCUMENTACION_TECNICA.md`:
     - “Modo desarrollo” vs “Modo producción”.
     - Cómo cambiar el número de workers según el número de cores del servidor (`workers = 2 * cores + 1` como regla aproximada).

---

### 3.3. Paso 2 – Introducir endpoints asíncronos en rutas de lectura intensiva

**Objetivo:** Empezar a aprovechar `async/await` de FastAPI en rutas sensibles a I/O, sin reescribir todo.

**Pasos:**

1. **Identificar endpoints de lectura frecuentes y no críticos de transacción**

   Ejemplos típicos:

   - `GET /api/v1/machines/`
   - `GET /api/v1/machines/{id}/availability`
   - `GET /api/v1/offers/my-offers`
   - `GET /api/v1/notifications/`
   - `GET /api/v1/watchlist/`

2. **Migrar estos endpoints a `async def`**

   - Cambiar firma de:

     ```python
     @router.get("/", response_model=List[MachineSchema])
     def read_machines(...):
         ...
     ```

     a:

     ```python
     @router.get("/", response_model=List[MachineSchema])
     async def read_machines(...):
         ...
     ```

3. **Evaluar uso de SQLAlchemy async**

   - A medio plazo (no en el primer sprint):
     - Migrar de `Session` síncrona a `AsyncSession` + `async_engine`.
     - Esto sí requiere más cambios (DAO, dependencias), por lo que puede planearse como una Fase 2.

4. **Beneficio inmediato**

   - Aunque la lógica siga usando SQLAlchemy sync, tener algunos endpoints async permitirá más fácil:
     - Integrar llamadas HTTP externas async (Maps, pagos futuros, etc).
     - Integrar drivers async en el futuro, sin cambiar firma pública.

---

### 3.4. Paso 3 – Configurar y usar Celery + Redis para tareas pesadas

**Objetivo:** Sacar del request/response tareas que pueden bloquear bajo carga (envío de notificaciones, procesos de subasta, generación de métricas pesadas).

**Pasos “LEGO”:**

1. **Definir un servicio `worker` en `docker-compose.yml`**

   Añadir:

   ```yaml
   worker:
     build: .
     command: celery -A app.services.celery_app worker --loglevel=INFO
     depends_on:
       - redis
       - db
   ```

   *(Ajustar ruta `celery_app` según implementes tu módulo Celery)*

2. **Crear módulo `app/services/celery_app.py`**

   - Esqueleto:

     ```python
     from celery import Celery
     from app.core.config import settings

     celery_app = Celery(
         "conmaq",
         broker=settings.REDIS_URL,
         backend=settings.REDIS_URL,
     )

     celery_app.conf.task_routes = {
         "app.services.tasks.*": {"queue": "default"},
     }
     ```

3. **Definir tareas en `app/services/tasks.py`**

   Ejemplos:

   - Enviar notificación (ya existe `services.notifications.send_notification`, se puede envolver).
   - Resolver subasta al cierre.
   - Recalcular métricas pesadas.

4. **Desde los endpoints, delegar trabajo**

   - Antes (sin Celery):

     ```python
     send_notification(db, user_id, type, title, message, payload)
     ```

   - Después:

     ```python
     from app.services.tasks import send_notification_task

     send_notification_task.delay(user_id, type, title, message, payload)
     ```

5. **Documentar en `DOCUMENTACION_TECNICA.md`**

   - Nueva sección: “Workers y Colas”.
   - Explicar:
     - Cómo arrancar el worker (`docker-compose up worker`).
     - Qué tipos de tareas mandamos a background.
     - Cómo monitorear con `flower` (ya está en `requirements.txt`, se puede agregar servicio `flower`).

---

### 3.5. Paso 4 – Implementar caché para endpoints de alta lectura

**Objetivo:** Reducir presión sobre la base de datos para datos que cambian poco o que se pueden cachear brevemente.

**Pasos:**

1. **Elegir endpoints candidatos**

   - `GET /machines/` (lista de máquinas).
   - `GET /metrics/financial` (podría cachearse 30–60s sin problema).
   - `GET /metrics/machines`.

2. **Crear módulo de caché simple con Redis**

   - `app/core/cache.py`:

     ```python
     import json
     import redis
     from app.core.config import settings

     redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

     def get_cache(key: str):
         value = redis_client.get(key)
         if value is None:
             return None
         return json.loads(value)

     def set_cache(key: str, value, ttl: int = 60):
         redis_client.set(key, json.dumps(value), ex=ttl)
     ```

3. **Usar caché en endpoints de métricas**

   - En `metrics.py`:

     ```python
     from app.core.cache import get_cache, set_cache

     @router.get("/financial")
     def get_financial_metrics(...):
         cache_key = "metrics:financial"
         cached = get_cache(cache_key)
         if cached is not None:
             return cached

         # calcular total_revenue y pending_revenue
         result = { ... }
         set_cache(cache_key, result, ttl=60)
         return result
     ```

4. **Documentar TTLs**

   - En la doc técnica, especificar:
     - Qué endpoints tienen caché.
     - Por cuánto tiempo.
     - Cómo invalidar si fuera necesario.

---

### 3.6. Paso 5 – Revisar y optimizar consultas SQL críticas

**Objetivo:** Asegurarse de que las operaciones de mayor uso estén soportadas por índices y consultas adecuadas.

**Pasos:**

1. **Catalogar consultas comunes**

   - A nivel de código (`DOCUMENTACION_TECNICA.md` ya lista varios endpoints).
   - Puntos importantes:
     - Filtrado de `machines` por estado, serial, etc.
     - Búsqueda de `availabilityslot` por `machine_id` + rango de fechas.
     - Listado de `offers` por `user_id` o `slot_id`.
     - `bookings` por `user_id` y estado.
     - `metrics` que usan `sum()` sobre tablas de `Booking` y `Transaction`.

2. **Verificar índices adecuados**

   - Ejemplo: para disponibilidad de una máquina en un período:

     - Consulta más probable:

       ```sql
       SELECT * FROM availabilityslot
       WHERE machine_id = ?
         AND start_time >= ?
         AND end_time <= ?
       ORDER BY start_time;
       ```

     - Índice ideal: índice compuesto (`machine_id`, `start_time`, `end_time`).
     - Plan:
       - Crear nueva migración Alembic que añada:
         ```python
         op.create_index(
             "ix_availabilityslot_machine_start_end",
             "availabilityslot",
             ["machine_id", "start_time", "end_time"],
             unique=False,
         )
         ```

3. **Analizar consultas de métricas**

   - `metrics.get_financial_metrics`:

     ```python
     total_revenue = db.query(func.sum(Transaction.amount)).filter(Transaction.status == "completed").scalar() or 0.0
     pending_revenue = db.query(func.sum(Booking.total_price)).filter(Booking.status == "pending_payment").scalar() or 0.0
     ```

   - Asegurarse de tener índices en:
     - `transaction.status`
     - `booking.status`

   - Si no existen, añadir con Alembic.

4. **Medir con `EXPLAIN` en Postgres**

   - En entorno de prueba, correr `EXPLAIN ANALYZE` sobre consultas pesadas.
   - Ajustar índices según resultados (evitar full table scans en tablas grandes).

---

### 3.7. Paso 6 – Establecer pruebas de carga mínimas

**Objetivo:** Validar empíricamente capacidad de respuesta bajo carga moderada, y detectar cuellos de botella.

**Pasos (pragmáticos):**

1. **Elegir herramienta de carga sencilla**

   - Recomendaciones:
     - `locust` (Python, muy legible).
     - o `k6` (script JS/TypeScript).

   Aquí propongo `locust` porque el stack ya es Python.

2. **Añadir `locust` como dev-dependency (opcional)**

   - En `backend/requirements.txt` o `requirements-dev.txt`:
     ```text
     locust>=2.0.0
     ```

3. **Crear archivo `backend/locustfile.py`**

   - Con escenarios básicos:

     - Listar máquinas.
     - Ver disponibilidad de una máquina.
     - Simular flujo de oferta + booking (solo para carga baja de prueba).

4. **Definir objetivo inicial**

   - Ejemplo:
     - 100 usuarios concurrentes.
     - RPS objetivo: ~50–100.
     - Latencia P95 < 300–400 ms para endpoints simples.

5. **Documentar resultados y ajustes**

   - Crear sección en `DOCUMENTACION_TECNICA.md` o un archivo `BACKEND_PERFORMANCE_NOTES.md`:

     - Escenario de prueba.
     - Resultados (RPS, P95, errores).
     - Ajustes posteriores (aumentar workers, agregar índices, ajustar caché).

---

### 3.8. Paso 7 – Preparar escalado horizontal y despliegue en Kubernetes (a nivel conceptual)

**Objetivo:** Tener lista la arquitectura para escalar horizontalmente cuando llegue el tráfico alto.

**Pasos de diseño (sin necesidad de implementarlo todo de inmediato):**

1. **Asegurar que la app es stateless**

   - Todas las sesiones/estado deben estar en:
     - DB (Postgres).
     - Redis (para rate limiting, caching, colas).
   - No usar memoria local del proceso para datos críticos o sesiones persistentes.

2. **Diseñar manifests de Kubernetes**

   - `Deployment` para `web` (FastAPI).
   - `Deployment` para `worker` (Celery).
   - `StatefulSet` o `Deployment` separado para `postgres` (o usar RDS/Cloud SQL).
   - `Deployment` para `redis`.
   - `HorizontalPodAutoscaler` para `web`.

3. **Anotar en documentación**

   - En `PRD_agendamiento.md` ya se habla de K8s.
   - Extender `DOCUMENTACION_TECNICA.md` con un diagrama:
     - `Ingress` → `web pods` → `db + redis`.
     - `worker pods` conectados a `redis` + `db`.

---

### 3.9. Paso 8 – Monitoreo y observabilidad

**Objetivo:** Poder detectar temprano problemas de rendimiento en producción.

**Pasos:**

1. **Integrar logs estructurados**

   - Configurar logging en `app/main.py` o `app/core/logging.py`.
   - Incluir:
     - Request ID.
     - Latencia del request.
     - Código de respuesta.

2. **Métricas básicas**

   - Usar Prometheus (o similar) para:
     - Contar requests por endpoint.
     - Medir duración de requests.
   - Incluso si no se implementa completo ahora, preparar hooks.

3. **Tracing (opcional a medio plazo)**

   - Integrar OpenTelemetry en `requirements.txt` y en la app.
   - Esto ayuda mucho cuando hay colas y varios servicios.

---

## Conclusión

El backend de CONMAQ está muy bien orientado hacia un sistema escalable:

- Usa FastAPI, Uvicorn, PostgreSQL y Redis.
- Tiene migraciones con índices básicos.
- Incorpora rate limiting.
- Documenta desde el principio un uso planificado de colas, workers, métricas y Kubernetes.

Hoy, sin embargo, está principalmente en modo **MVP robusto de desarrollo**, todavía sin:

- Config de servidor de producción con múltiples workers.
- Uso amplio de asincronía en endpoints.
- Caché de lectura.
- Workers Celery operativos.
- Pruebas de carga documentadas.

Por eso la calificación **6/10**: mejor que “básico”, con decisiones correctas para crecer, pero aún sin las optimizaciones y validaciones necesarias para llamarlo “alto rendimiento” en producción.

Siguiendo el plan paso a paso descrito (modo prod de Uvicorn/Gunicorn, endpoints async, Celery, caché, índices compuestos, pruebas de carga, y preparación para K8s/horizontal scaling), el proyecto puede subir gradualmente a **8–9/10**, y más adelante acercarse al nivel **10/10** para entornos de alta concurrencia real.