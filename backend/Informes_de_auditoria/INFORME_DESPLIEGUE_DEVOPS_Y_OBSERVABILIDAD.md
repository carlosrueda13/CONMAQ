# Informe de Auditoría – Despliegue, DevOps y Observabilidad (Backend CONMAQ)

## 1. Calificación

**Calificación global en “Despliegue, DevOps y Observabilidad”: _4 / 10_**

---

## 2. Explicación de la calificación

### 2.1. Resumen ejecutivo

El backend de CONMAQ tiene **buenas bases de DevOps a nivel de desarrollo local**:

- Está **containerizado** con Docker:
  - `backend/Dockerfile`
  - `backend/docker-compose.yml` con servicios `web`, `db`, `redis`.
- Usa **Alembic** para migraciones de base de datos:
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - Múltiples migraciones en `backend/alembic/versions/*.py`.
- Hay una estructura clara para ejecución de tests con `pytest` y está presente en `requirements.txt`.

Sin embargo, **no se ve en el repositorio**:

- Ningún pipeline de **CI/CD** (no hay `.github/workflows/*.yml`, ni GitLab, ni Jenkins declarados).
- Scripts o manifests de despliegue a entornos remotos (staging/producción) más allá de `docker-compose.yml` local.
- Instrumentación de **observabilidad real** (Prometheus, OpenTelemetry, dashboards, alertas) más allá de conceptos escritos en el PRD.
- Configuración de logs estructurados o agregación/centralización de logs (solo logs estándar a stdout/controlados por Uvicorn/Alembic por defecto).

Esto sitúa al proyecto en la banda:

> **2–4: Automatización básica.** Se usan contenedores o VMs, pero sin integración continua establecida. Las pruebas se corren manualmente. Logs básicos, sin monitoreo/alertas.

Lo que **eleva la calificación hacia el 4** (y no 2–3) es:

- Buena containerización reproducible (`Dockerfile` y `docker-compose.yml` claros).
- Uso completo de Alembic para versionar el esquema de la DB.
- Plan de desarrollo (`PLAN_DESARROLLO.md`) y PRD (`PRD_agendamiento.md`) que **definen** una visión de CI/CD y observabilidad, aunque aún no implementada en código.

No alcanza 5–6 porque:

- No hay ninguna evidencia de pipeline de CI en el repositorio.
- No hay scripts de despliegue remoto ni separación staging/producción.
- Observabilidad (métricas, trazas, dashboards) está solo en el PRD, no en la implementación.

---

### 2.2. Puntos fuertes actuales

#### 2.2.1. Containerización y entorno reproducible

**Archivos clave:**

- `backend/Dockerfile`:

  ```dockerfile
  FROM python:3.11-slim

  WORKDIR /app

  ENV PYTHONDONTWRITEBYTECODE 1
  ENV PYTHONUNBUFFERED 1

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port",  "8000", "--reload"]
  ```

- `backend/docker-compose.yml`:

  ```yaml
  version: '3.8'

  services:
    web:
      build: .
      command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
      volumes:
        - .:/app
      ports:
        - "8000:8000"
      environment:
        - DATABASE_URL=postgresql://postgres:postgres@db:5432/agendamiento
        - REDIS_URL=redis://redis:6379/0
        - SECRET_KEY=changethis_secret_key_for_dev
        - ALGORITHM=HS256
        - ACCESS_TOKEN_EXPIRE_MINUTES=30
      depends_on:
        - db
        - redis

    db:
      image: postgres:15-alpine
      volumes:
        - postgres_data:/var/lib/postgresql/data
      environment:
        - POSTGRES_USER=postgres
        - POSTGRES_PASSWORD=postgres
        - POSTGRES_DB=agendamiento
      ports:
        - "5433:5432"

    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"

  volumes:
    postgres_data:
  ```

**Fortalezas:**

- Entorno de desarrollo **auto-contenido** (API + Postgres + Redis).
- Parámetros clave (`DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`) vienen de `environment`, permitiendo override por entorno.
- `postgres_data` como volumen persistente → datos sobreviven reinicios.

Esto significa que un desarrollador nuevo puede levantar todo con:

```bash
cd backend
docker-compose up --build
```

→ Ya es una gran mejora respecto a un proyecto sin Docker (calificación >1-2).

#### 2.2.2. Gestión de esquema de base de datos con Alembic

**Archivos clave:**

- `backend/alembic.ini`
- `backend/alembic/env.py`
- Migraciones en `backend/alembic/versions/*.py`:
  - `67fca4266a95_initial_migration.py`
  - `bba41f562bcc_add_serial_number_to_machines.py`
  - `3db25977c22c_add_offer_model_and_update_.py`
  - `6d495d6029a4_add_watchlist_and_notification_models.py`
  - `1fb859e04cdb_add_booking_table.py`
  - `7a25e71a7f05_add_transaction_table.py`

**Fortalezas:**

- Esquema versionado y reproducible:
  - `upgrade()` / `downgrade()` definidos.
  - Índices creados explícitamente (ej. `ix_machine_serial_number`, `ix_offer_id`…).
- `alembic/env.py` usa `settings.DATABASE_URL`:

  ```python
  from app.db.base import Base
  from app.core.config import settings
  ...
  configuration["sqlalchemy.url"] = settings.DATABASE_URL
  ```

- `DOCUMENTACION_TECNICA.md` documenta cómo ejecutar:

  ```bash
  POSTGRES_SERVER=localhost POSTGRES_PORT=5433 alembic upgrade head
  ```

Esto aporta mucho a:

- **Reproducibilidad de despliegues** (migraciones consistentes entre entornos).
- Facilidad para incorporar cambios de esquema en cualquier pipeline de CI/CD futuro.

#### 2.2.3. Requirements claros, incluyendo herramientas de test y worker

`backend/requirements.txt`:

```text
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.23
alembic>=1.12.1
psycopg2-binary>=2.9.9
pydantic>=2.8.0
pydantic-settings>=2.1.0
PyJWT>=2.8.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
email-validator>=2.1.0.post1
tenacity>=8.2.3
redis>=5.0.1
celery>=5.3.6
flower>=2.0.1
httpx>=0.25.2
pytest>=7.4.3
slowapi>=0.1.9
Faker>=20.1.0
```

**Fortalezas:**

- Lista de dependencias necesaria para:
  - API (FastAPI, Uvicorn, SQLAlchemy, Pydantic).
  - Seguridad (JWT, bcrypt).
  - Background/colas (`redis`, `celery`, `flower`).
  - Testing (`pytest`).
- Esto facilita la instalación en cualquier entorno (CI, staging, prod) de forma determinista.

#### 2.2.4. Visión clara de DevOps y observabilidad en documentación

`PRD_agendamiento.md` y `PLAN_DESARROLLO.md` incluyen:

- En PRD:

  - Requerimientos no funcionales:
    - Seguridad: HTTPS, OWASP, rate limiting, logs de auditoría.
    - Observabilidad: logs JSON, Prometheus, OpenTelemetry, alerting.
    - CI/CD: GitHub Actions con lint, tests, build, deploy.
- En PLAN_DESARROLLO (Día 4):

  - Seguridad y calidad:
    - Rate Limiting.
    - CORS restrictivo.
    - Headers de seguridad.
    - Tests (unitarios e integrados).

Esto es valioso porque:

- Hay una **hoja de ruta** clara para llegar a un 7–9/10.
- Aunque no se vea aún implementado, las decisiones futuras estarán alineadas.

---

### 2.3. Debilidades según la rúbrica

#### 2.3.1. Falta de CI/CD implementado en el repo

- No hay `.github/workflows/` ni otros pipelines de CI vistos en los archivos aportados.
- `.vscode/settings.json` solo indica:

  ```json
  {
      "python.testing.pytestArgs": [
          "alembic"
      ],
      "python.testing.unittestEnabled": false,
      "python.testing.pytestEnabled": true
  }
  ```

  lo cual parece una configuración local, tal vez errónea (apunta a `alembic` en vez de `app` o `tests`), pero en todo caso **no es CI**.

Impacto:

- Tests, lint, etc. deben lanzarse manualmente.
- El despliegue a producción (si existe) no está codificado en este repo.

Según la rúbrica, para llegar a **5–6** se requiere:

> “Hay un pipeline (GitHub Actions, GitLab CI, Jenkins) que ejecuta compilación, tests y despliega en staging.”

Esto por ahora **no está**.

#### 2.3.2. Despliegue enfocado a desarrollo local

- `Dockerfile` y `docker-compose.yml` lanzan Uvicorn con `--reload`, pensado explícitamente para desarrollo:

  ```dockerfile
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  ```

- No hay:
  - Comando alternativo de producción (p. ej. Gunicorn + UvicornWorker).
  - Definición de entornos `staging` vs `production`.

Impacto:

- El stack actual es excelente para desarrollo local, pero:
  - No es adecuado tal cual para producción (falta TLS, workers apropiados, restart policy, etc.).
  - No hay “scripts de infraestructura” para levantar un entorno remoto reproducible (Kubernetes, terraform, etc.).

#### 2.3.3. Observabilidad declarada pero no instrumentada

- `PRD_agendamiento.md` pide:

  - Logs estructurados (JSON).
  - Metrics: Prometheus counters.
  - Tracing con OpenTelemetry.
  - Alerting.

- En el código:

  - Uvicorn y Alembic generan logs por defecto (no estructurados).
  - No se ve:
    - Middleware de logging propio.
    - Endpoints de metrics (`/metrics`) para Prometheus.
    - Instrumentación con OpenTelemetry.

Impacto:

- En producción, no habría:
  - Latencias por endpoint.
  - Conteos de errores.
  - Trazas de requests complejos (subasta, pagos, bookings).

Esto encaja con la banda 2–4: “logs básicos, sin agregación ni monitoreo real”.

#### 2.3.4. Sin scripts de despliegue automatizados o IaC

- No se ve:
  - `k8s/` con manifests.
  - `terraform/`, `ansible/`, `pulumi/`.
- Solo `docker-compose.yml`.

Impacto:

- El despliegue a un PaaS o cluster K8s debería definirse “a mano” en cada entorno.
- No hay “infraestructura como código” que garantice reproducibilidad y mínima deriva de configuración.

---

## 3. Plan detallado de mejoras y correcciones  
*(Muy detallado, paso a paso – instrucciones accionables sobre este repo)*

### 3.1. Objetivo global

1. Subir de **4/10** a al menos **6–7/10** en Despliegue, DevOps y Observabilidad.
2. Hacerlo en fases incrementales:
   - Fase 1: CI básico + tests.
   - Fase 2: Build & Deploy reproducible (staging/prod).
   - Fase 3: Observabilidad (logs, métricas, trazas).
3. Usar y extender lo que ya existe: Docker + Alembic + documentación actual.

---

### 3.2. Paso 1 – Crear un pipeline de CI mínimo con GitHub Actions

**Objetivo:** Que cada push/PR ejecute tests (y en el futuro lint, type-check, etc.).

**Pasos:**

1. **Crear directorio de workflows**

   En la raíz del repo (no solo en `backend/`):

   ```bash
   mkdir -p .github/workflows
   ```

2. **Crear workflow `backend-ci.yml`**

   Archivo: `.github/workflows/backend-ci.yml`

   Contenido sugerido (versión mínima):

   ```yaml
   name: Backend CI

   on:
     push:
       paths:
         - "backend/**"
     pull_request:
       paths:
         - "backend/**"

   jobs:
     test:
       runs-on: ubuntu-latest
       defaults:
         run:
           working-directory: backend
       steps:
         - uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: "3.11"

         - name: Install dependencies
           run: |
             pip install --no-cache-dir -r requirements.txt

         - name: Run tests
           run: |
             pytest
   ```

3. **Actualizar documentación**

   - En `DOCUMENTACION_TECNICA.md`, sección 10 (Testing y Despliegue):
     - Añadir subsección “Integración Continua (GitHub Actions)”.
     - Explicar que en cada push/PR a ramas relevantes:
       - Se ejecuta `pytest`.
       - (Más adelante) se añadirán linters y coverage.

4. **Beneficio inmediato**

   - Garantiza que la suite de tests (cuando la haya) se ejecuta en cada cambio.
   - Es el requisito mínimo para entrar en la banda **5–6** de la rúbrica.

---

### 3.3. Paso 2 – Añadir build de imagen Docker en CI

**Objetivo:** Asegurar que la imagen Docker siempre construye correctamente con la versión actual del código.

**Pasos:**

1. **Extender `backend-ci.yml` con un job de build**

   Añadir un segundo job:

   ```yaml
   jobs:
     test:
       ...
     build:
       runs-on: ubuntu-latest
       needs: test
       defaults:
         run:
           working-directory: backend
       steps:
         - uses: actions/checkout@v4

         - name: Build Docker image
           run: |
             docker build -t conmaq-backend:ci .
   ```

2. **Futuro (opcional): push a registry**

   - Cuando haya un registry (Docker Hub, GHCR), añadir:
     - Login (`docker login ...` con secrets de GH Actions).
     - `docker tag` y `docker push`.

3. **Documentar**

   - Indicar que:
     - Cada cambio verificado por tests produce una imagen Docker “buildable”.
     - Esto reduce sorpresas al desplegar.

---

### 3.4. Paso 3 – Definir configuración de despliegue para producción/staging

**Objetivo:** Tener una historia clara de cómo se despliega la app en un entorno remoto, incluso si manual al principio.

**Pasos:**

1. **Crear un `docker-compose.prod.yml` de ejemplo**

   Archivo: `backend/docker-compose.prod.yml` (ejemplo para server simple con reverse proxy puede ser posterior, pero mínimo se puede definir):

   ```yaml
   version: '3.8'

   services:
     web:
       image: conmaq-backend:latest  # asumimos imagen ya construida y subida
       command: gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
       environment:
         - DATABASE_URL=${DATABASE_URL}
         - REDIS_URL=${REDIS_URL}
         - SECRET_KEY=${SECRET_KEY}
         - ALGORITHM=HS256
         - ACCESS_TOKEN_EXPIRE_MINUTES=30
       depends_on:
         - db
         - redis

     db:
       image: postgres:15-alpine
       ...

     redis:
       image: redis:7-alpine
       ...

   volumes:
     postgres_data:
   ```

   *(Los detalles exactos pueden variar; lo importante es que exista un “modo prod” sin `--reload`.)*

2. **Separar entornos vía variables**

   - Definir en la doc:
     - `.env.dev` para desarrollo.
     - `.env.prod` para producción (no committeado, solo ejemplo `.env.example`).

3. **Documentar proceso de despliegue manual reproducible**

   - En `DOCUMENTACION_TECNICA.md`, agregar sección:

     > “Despliegue en Producción (Manual Inicial)”
     >
     > 1. Construir imagen y subir a registry.
     > 2. En servidor, obtener `.env.prod`.
     > 3. Correr `docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d`.

---

### 3.5. Paso 4 – Instrumentar logs estructurados

**Objetivo:** Pasar de logs “por defecto” a logs estructurados, aprovechables por ELK/Loki en el futuro.

**Pasos:**

1. **Configurar logging en `app/main.py` o nuevo módulo `app/core/logging_config.py`**

   Ejemplo minimalista (pseudo):

   ```python
   import logging
   import sys
   import json
   from uvicorn.logging import DefaultFormatter

   def configure_logging():
       handler = logging.StreamHandler(sys.stdout)
       formatter = DefaultFormatter(fmt="%(levelname)s %(message)s", use_colors=False)
       handler.setFormatter(formatter)

       logger = logging.getLogger()
       logger.setLevel(logging.INFO)
       logger.handlers = [handler]
   ```

   - O mejor: usar un formatter JSON custom.

2. **Llamar `configure_logging()` al inicializar la app**

   En `app/main.py` antes de `app = FastAPI(...)`:

   ```python
   from app.core.logging_config import configure_logging
   configure_logging()
   ```

3. **Agregar un middleware simple de access-log (opcional)**

   - Ver idea en informe de seguridad (AccessLogMiddleware).

4. **Documentar**

   - Describir en el manual:
     - Formato de logs.
     - Campos presentes.
     - Cómo filtrarlos desde un agregador (cuando se añada).

---

### 3.6. Paso 5 – Exponer métricas básicas para Prometheus

**Objetivo:** Poner bases reales de observabilidad numérica (latencias, conteos, errores).

**Pasos (sencillos):**

1. **Agregar dependencia `prometheus_client`**

   - Añadir a `requirements.txt`:

     ```text
     prometheus_client>=0.20.0
     ```

2. **Crear endpoint `/metrics`**

   - Archivo nuevo `app/api/metrics_exporter.py`:

     ```python
     from fastapi import APIRouter, Response
     from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

     router = APIRouter()

     @router.get("/metrics")
     def metrics():
         data = generate_latest()
         return Response(content=data, media_type=CONTENT_TYPE_LATEST)
     ```

   - Incluir en `app/main.py` o en `app/api/v1/api.py` (este segundo sería `/api/v1/metrics` pero conviene exponer `/metrics` a nivel root para Prometheus).

3. **Instrumentar un par de contadores/gauges**

   - Por ejemplo, en `app/main.py` o en un middleware:

     ```python
     from prometheus_client import Counter

     REQUEST_COUNT = Counter(
         "conmaq_requests_total", "Total HTTP requests", ["method", "path", "status"]
     )
     ```

   - En un middleware de requests:

     ```python
     from starlette.middleware.base import BaseHTTPMiddleware

     class PrometheusMiddleware(BaseHTTPMiddleware):
         async def dispatch(self, request, call_next):
             response = await call_next(request)
             REQUEST_COUNT.labels(
                 method=request.method,
                 path=request.url.path,
                 status=response.status_code,
             ).inc()
             return response
     ```

   - Añadir `app.add_middleware(PrometheusMiddleware)`.

4. **Documentar en PRD/Manual**

   - Indicar que `/metrics` ya expone datos que Prometheus puede scrapear.

---

### 3.7. Paso 6 – Integrar observabilidad en el roadmap (OpenTelemetry)

**Objetivo:** No necesariamente instrumentar todo ya, pero preparar el terreno.

**Pasos:**

1. **Agregar una nota en `PRD_agendamiento.md` y `DOCUMENTACION_TECNICA.md`**

   - En secciones de Observabilidad:
     - Precisar que se usará `OpenTelemetry` + exportador (OTLP, Jaeger, etc.).
     - Definir prioridades de trazado:
       - Subastas (bidding).
       - Flujo oferta → booking → pago.

2. **Futuro (cuando sea prioritario)**

   - Añadir `opentelemetry-instrumentation-fastapi` y configurar en `main.py`.

---

### 3.8. Paso 7 – Añadir pasos de despliegue a CI/CD (cuando haya infra remota)

**Objetivo:** Avanzar hacia banda 7–9 de la rúbrica (deploy automatizado).

**Pasos (alto nivel):**

1. **Decidir proveedor de despliegue**

   - Ejemplos:
     - Kubernetes (EKS/GKE/AKS).
     - PaaS (Render, Fly.io, Heroku-like).
   - Dependiendo de la elección:
     - Crear manifests K8s en `/k8s`.
     - O scripts de deploy a PaaS.

2. **Extender pipeline de CI para CD**

   - Después del job `build`, añadir job `deploy`:

     ```yaml
     deploy:
       runs-on: ubuntu-latest
       needs: build
       steps:
         - name: Deploy to staging
           run: |
             # comandos contra cluster o PaaS
     ```

3. **Separar entornos**

   - Al menos:
     - `staging` (deploy en cada merge en `develop`).
     - `production` (deploy manual/approval desde `main` o tag).

4. **Alertas básicas**

   - Integrar con monitor (Prometheus + Alertmanager, o el stack propio del proveedor).
   - Como mínimo:
     - Alerta si API cae.
     - Alerta si ratio de errores 5xx supera un umbral.

---

### 3.9. Paso 8 – Resumen de “roadmap” de madurez DevOps

Para visualizar el progreso:

1. **Fase inmediata (subir a 5–6/10):**

   - CI con `pytest` + build de imagen.
   - Config prod básica (`docker-compose.prod.yml` sin `--reload`).
   - Logs estructurados.
   - Endpoint `/metrics` + contadores básicos.

2. **Fase intermedia (hacia 7–8/10):**

   - Despliegue automatizado a staging/prod (CI/CD completo).
   - Manifests K8s o scripts de PaaS versionados.
   - Más métricas de negocio (nº de ofertas, bookings, revenue por tiempo) en Prometheus.
   - Alertas primitivas (uptime, error rate).

3. **Fase avanzada (9–10/10):**

   - OpenTelemetry con trazas distribuidas.
   - Dashboards en Grafana (SLO/SLI: latencia, error ratio, bookings/minuto).
   - Blue/green o canary releases.
   - Infra como código completa (Terraform + K8s).
   - Postmortems y procesos de incident management.

---

## Conclusión

Actualmente, el backend de CONMAQ se ubica en **4/10** en Despliegue, DevOps y Observabilidad:

- Muy buena **base local** (Docker, docker-compose, Alembic, requirements claros).
- Excelentes **intenciones documentadas** (PRD y Plan de Desarrollo).
- Pero aún falta:

  - Integración continua real.
  - Automatización de despliegue.
  - Instrumentación de observabilidad más allá de los logs default.

El plan propuesto, paso a paso, permite evolucionar de forma incremental hacia un entorno:

- Con CI/CD robusto.
- Con despliegues reproducibles entre entornos.
- Con observabilidad suficiente para entender y operar la plataforma bajo carga real.

Siguiendo este roadmap, el proyecto podría alcanzar **6–7/10** en el corto plazo y aspirar a **8–9/10** una vez que se completen los pasos de CD, Kubernetes/PaaS y observabilidad avanzada.