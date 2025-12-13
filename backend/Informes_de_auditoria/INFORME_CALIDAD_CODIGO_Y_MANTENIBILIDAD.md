# Informe de Auditoría – Calidad del Código y Mantenibilidad (Backend CONMAQ)

## 1. Calificación

**Calificación global en “Calidad del Código y Mantenibilidad”: _6 / 10_**

---

## 2. Explicación de la calificación

### 2.1. Resumen ejecutivo

El backend de CONMAQ muestra una **calidad de código general buena**, con:

- Estructura clara de módulos (`app/core`, `app/api`, `app/models`, `app/schemas`, `app/db`).
- Uso adecuado de **type hints** en la mayoría de los endpoints (ej. `-> Any`, `-> List[Schema]`, `db: Session`).
- Código relativamente corto en los endpoints y funciones, con **responsabilidades bastante claras**.
- Documentación técnica muy detallada en `DOCUMENTACION_TECNICA.md` que ayuda fuertemente a la mantenibilidad.
- Configuración explícita de `Settings` vía `pydantic-settings` (`app/core/config.py`), lo que favorece claridad y centralización de configuración.

Sin embargo, para aspirar a un 7–9 (alta calidad) según la rúbrica, se detectan carencias importantes:

- No se observa en el repositorio un **directorio de tests** (`tests/`) ni archivos de pruebas (`test_*.py`).
- No hay señales claras de **mypy**, linters (flake8, ruff), ni formateadores (black, isort) configurados en el repo (no se ven `pyproject.toml`, `.flake8`, `.pre-commit-config.yaml`, etc.).
- No se ve configuración de **CI** que ejecute linters + tests (por ejemplo, workflows de GitHub Actions en `.github/workflows` para backend).
- No hay un archivo claro de **gestión de dependencias** del backend (p. ej. `requirements.txt` o `pyproject.toml` específico en `backend/`).

Esto ubica el proyecto sólidamente en la franja:

> **5–6: Calidad aceptable.** Se aplican linters/formateo (PEP 8), uso de tipado básico, cierta aplicación de SOLID, pero con carencias en pruebas automatizadas amplias y herramientas de análisis estático.

Dado que:

- A nivel de **estilo** y estructura el código está bastante bien.
- Pero **faltan claramente test automatizados y tooling de calidad** al nivel de la rúbrica 7–9.

La calificación razonable es **6/10**: código bien organizado y legible, pero sin el ecosistema de calidad (tests, linters, CI) necesario para ser “alta calidad” en producción.

---

### 2.2. Evidencias positivas de calidad y mantenibilidad

#### 2.2.1. Código siguiendo PEP8 y buenas prácticas generales

A partir de los fragmentos:

- `app/api/v1/endpoints/users.py`
- `app/api/v1/endpoints/watchlist.py`
- `app/api/v1/endpoints/notifications.py`
- `app/api/v1/endpoints/metrics.py`
- `app/core/config.py`
- `app/main.py`

se observa:

- **Nombres de variables descriptivos**: `current_user`, `total_revenue`, `pending_revenue`, `SessionLocal`, etc.
- **Imports ordenados razonablemente** y sin código muerto evidente.
- **Identación consistente con 4 espacios**, sin mezcla de tabs.
- Funciones relativamente cortas y enfocadas, por ejemplo:

  ```python
  @router.post("/", response_model=UserSchema)
  @limiter.limit("5/minute")
  def create_user(
      *,
      request: Request,
      db: Session = Depends(deps.get_db),
      user_in: UserCreate,
  ) -> Any:
      """
      Create new user.
      """
      user = db.query(User).filter(User.email == user_in.email).first()
      if user:
          raise HTTPException(
              status_code=400,
              detail="The user with this username already exists in the system.",
          )
      
      db_obj = User(
          email=user_in.email,
          hashed_password=security.get_password_hash(user_in.password),
          full_name=user_in.full_name,
          phone=user_in.phone,
          role=user_in.role,
          is_superuser=user_in.is_superuser,
      )
      db.add(db_obj)
      db.commit()
      db.refresh(db_obj)
      return db_obj
  ```

- Comentarios y docstrings en endpoints explicando propósito (`"""Create new user."""`, `"Retrieve current user's watchlist."`).

Todo esto denota **buen cuidado en la legibilidad**.

#### 2.2.2. Uso de tipado estático básico (type hints)

- En endpoints vemos consistentemente:

  - Parámetros tipados: `db: Session`, `current_user: User`, `skip: int = 0`, `limit: int = 100`.
  - Tipos de retorno: `-> Any`, `-> List[NotificationSchema]`, `-> List[WatchlistSchema]`.

- En `app/core/config.py`:

  ```python
  class Settings(BaseSettings):
      PROJECT_NAME: str = "Agendamiento API"
      API_V1_STR: str = "/api/v1"
      ...
      POSTGRES_PORT: str = "5433"
      DATABASE_URL: Optional[str] = None
  ```

Esto facilita el uso posterior de **mypy** si se integra, y mejora la comprensión al leer código.

#### 2.2.3. Separación razonable de responsabilidades (pre-SOLID)

Aunque no se ve una capa de “servicios” muy formal, se observan:

- Modelos de base de datos en `app/models`.
- Esquemas de Pydantic en `app/schemas`.
- Dependencias (auth, DB, roles) centralizadas en `app/api/deps.py`.
- Endpoints principalmente haciendo:
  - Orquestación de dependencias.
  - Llamadas a la base de datos/servicios.
  - Retorno de esquemas.

Esto es ya una buena base de **single responsibility** por módulo y función, aunque se puede refinar más (ver plan en sección 3).

#### 2.2.4. Documentación técnica extensa y útil

`backend/DOCUMENTACION_TECNICA.md`:

- Describe módulos, funciones, modelos, endpoints, dependencias.
- Funciona casi como una **guía de onboarding técnico** para nuevos devs.
- Permite entender el “por qué” de muchas decisiones de diseño sin leer todo el código.

Esto es un enorme plus para **mantenibilidad**, aunque la rúbrica de “Calidad de código y Mantenibilidad” apunta también a tests y tooling automático, que aún faltan.

---

### 2.3. Principales puntos débiles según la rúbrica

#### 2.3.1. Ausencia (o al menos no visible) de pruebas automatizadas

En el repositorio:

- No se ve una carpeta `tests/` dentro de `backend/`.
- No se observan archivos `test_*.py` ni `conftest.py`.
- En `PRD_agendamiento.md` se mencionan explícitamente:

  ```markdown
  - **Tests:** pytest, cobertura mínima de 70% para lógica crítica (booking, ofertas, pagos).
  ```

  Pero esa intención aún no se ve concretada en el código.

Impacto según rúbrica:

- Sin test automatizados la mantenibilidad se resiente:
  - Cada refactor puede romper funcionalidad crítica sin detección temprana.
  - Es difícil garantizar que la lógica compleja (subastas, bookings, pagos) se mantenga correcta en el tiempo.

Esto impide subir la calificación a 7–9, donde se esperan:

> “Las pruebas unitarias e integradas cubren la mayoría del código crítico (tests en cada feature, cobertura alta) y se actualizan con CI.”

#### 2.3.2. Falta de herramientas de análisis estático y formateo automático integradas

- No se encuentran:
  - `pyproject.toml` con secciones de `black`, `ruff`, `mypy`, `pytest`.
  - Archivos `.flake8`, `.isort.cfg`, `.pre-commit-config.yaml`.
- Tampoco un `requirements-dev.txt` o similar donde se definan dependencias de desarrollo (`pytest`, `mypy`, `flake8`, etc.).

Aunque el estilo del código es bueno, falta:

- Garantía de consistencia a través de **herramientas automáticas**, lo que:
  - Aumenta el riesgo de divergencia de estilo cuando entre más gente al equipo.
  - Añade fricción a revisión de código (se revisa forma y fondo al mismo tiempo).

#### 2.3.3. Gestión de dependencias y seguridad

- No se ve un archivo de dependencias específico para el backend (p. ej., `backend/requirements.txt` o `pyproject.toml`).
- Tampoco un **lock file** (como `poetry.lock`, `requirements.txt` con versiones fijadas y revisadas).

Según la rúbrica de 7–10, se espera:

- Gestión de dependencias segura.
- Bloqueo de versiones en producción.
- Integración con análisis de seguridad (SCA).

Actualmente, esto no está claramente implementado.

#### 2.3.4. Ausencia visible de CI para calidad de código

- `PRD_agendamiento.md` habla de:

  ```markdown
  - **CI/CD:** GitHub Actions con lint, tests, build, deploy.
  ```

- Pero no se ven workflows (`.github/workflows/*.yml`) específicos para el backend ejecutando:
  - `pytest`
  - `mypy`
  - `flake8/ruff`
  - `black --check`

La falta de CI para calidad y tests reduce la **confiabilidad** de la base de código conforme crece.

---

## 3. Plan detallado de mejoras y correcciones  
*(Estilo paso a paso)*

### 3.1. Objetivo general del plan

1. Pasar de **6/10 a 8–9/10** en Calidad del Código y Mantenibilidad.
2. Hacerlo sin reescribir el backend, sino añadiendo:
   - Tests sistemáticos.
   - Tooling de calidad (linters, formateadores, type checkers).
   - Integración CI.
   - Gestión de dependencias sólida.

---

### 3.2. Paso 1 – Definir y fijar dependencias del backend

**Objetivo:** Tener un archivo fuente de verdad para dependencias + un lock claro para producción.

**Pasos:**

1. **Crear archivo `backend/requirements.in` o lista base**

   Ejemplo mínimo (ajustar según lo que ya se usa):

   ```text
   fastapi
   uvicorn[standard]
   sqlalchemy
   psycopg2-binary
   pydantic
   pydantic-settings
   python-jose[cryptography]
   passlib[bcrypt]
   slowapi
   redis
   alembic
   ```

2. **Crear archivo `backend/requirements-dev.in`**

   Incluir herramientas de desarrollo:

   ```text
   pytest
   httpx
   pytest-asyncio
   coverage
   mypy
   black
   isort
   ruff
   ```

3. **Generar `requirements.txt` y `requirements-dev.txt` (si se usa pip-tools)**

   - Opcionalmente usar `pip-compile`:
     - `pip-compile backend/requirements.in -o backend/requirements.txt`
     - `pip-compile backend/requirements-dev.in -o backend/requirements-dev.txt`
   - Si no se usa pip-tools, al menos fijar versiones manualmente:

     ```text
     fastapi==0.115.0
     sqlalchemy==2.0.25
     ...
     ```

4. **Actualizar `DOCUMENTACION_TECNICA.md`**

   - Añadir sección: “Gestión de dependencias”.
   - Explicar cómo instalar:

     ```bash
     pip install -r backend/requirements.txt
     pip install -r backend/requirements-dev.txt
     ```

---

### 3.3. Paso 2 – Introducir estructura básica de tests

**Objetivo:** Tener una base mínima de pruebas automatizadas preparada para crecer.

**Pasos:**

1. **Crear estructura de carpetas de tests**

   Dentro de `backend/`:

   ```bash
   mkdir -p backend/tests/api/v1
   mkdir -p backend/tests/services
   mkdir -p backend/tests/models
   touch backend/tests/__init__.py
   ```

2. **Crear un `conftest.py` mínimo**

   En `backend/tests/conftest.py`:

   - Definir:
     - `client` de `TestClient(FastAPI)`.
     - Una base de datos de pruebas (por ejemplo SQLite en memoria) y override de `get_db`.
   - Ejemplo (esqueleto):

     ```python
     import pytest
     from fastapi.testclient import TestClient
     from app.main import app
     from app.api import deps
     from app.db.session import SessionLocal

     @pytest.fixture
     def db_session():
         db = SessionLocal()
         try:
             yield db
         finally:
             db.close()

     @pytest.fixture
     def client(db_session):
         def _get_test_db():
             try:
                 yield db_session
             finally:
                 pass

         app.dependency_overrides[deps.get_db] = _get_test_db
         with TestClient(app) as c:
             yield c
     ```

     *(Esto es un ejemplo conceptual; ajustar a cómo se crea la sesión y la DB en el proyecto).*

3. **Crear primeros tests de smoke para endpoints clave**

   - `backend/tests/api/v1/test_health.py` (si existe health endpoint; si no, crear luego).
   - `backend/tests/api/v1/test_auth.py`: probar login y flujo básico.
   - `backend/tests/api/v1/test_machines.py`: crear y listar máquinas (si hay endpoints).

4. **Incluir en `PLAN_DESARROLLO.md` una mini-sección “Testing”**

   - Describir qué se espera cubrir en cada fase.
   - Marcar explícitamente:
     - Lógica de subastas (bidding).
     - Booking conversion.
     - Pagos (transactions).

---

### 3.4. Paso 3 – Añadir coverage y objetivo de cobertura

**Objetivo:** Alinear con el PRD: “cobertura mínima de 70% para lógica crítica”.

**Pasos:**

1. **Configurar coverage**

   - Crear `backend/.coveragerc`:

     ```ini
     [run]
     branch = True
     source =
         app

     [report]
     show_missing = True
     skip_covered = True
     ```

2. **Definir comando estándar de tests en la documentación**

   En `DOCUMENTACION_TECNICA.md`, sección Testing:

   ```bash
   cd backend
   pytest --cov=app --cov-report=term-missing
   ```

3. **Meta de corto plazo**

   - Primera meta: **>40%** cobertura en lógica crítica (offers, bookings, payments).
   - Meta de mediano plazo: **≥70%** en módulos clave (como define el PRD).

---

### 3.5. Paso 4 – Integrar linters, formatter y type checker

**Objetivo:** Que el estilo y la corrección básica del código sean garantizadas automáticamente.

**Pasos:**

1. **Configurar `black`, `isort`, `ruff`, `mypy`**

   - Crear `backend/pyproject.toml` o, si no se quiere unificar, archivos de config:

     - `backend/pyproject.toml` (ejemplo):

       ```toml
       [tool.black]
       line-length = 88
       target-version = ["py311"]

       [tool.isort]
       profile = "black"

       [tool.ruff]
       line-length = 88
       target-version = "py311"
       select = ["E", "F", "W", "B", "UP"]
       ignore = ["E501"]  # si se deja a black manejar largo

       [tool.mypy]
       python_version = "3.11"
       strict = false
       ignore_missing_imports = true
       disallow_untyped_defs = false
       ```

2. **Añadir scripts de conveniencia**

   - En `DOCUMENTACION_TECNICA.md` o en un `Makefile`:

     ```bash
     # Formatear
     black app
     isort app

     # Lint
     ruff check app

     # Type check
     mypy app
     ```

3. **Ejecución periódica**

   - Establecer en el flujo de trabajo del equipo que:
     - Antes de abrir PR se ejecute `black`, `isort`, `ruff`, `mypy`.
   - Con el tiempo, endurecer las reglas (por ejemplo, activar `disallow_untyped_defs` en mypy en módulos nuevos).

---

### 3.6. Paso 5 – Configurar CI (GitHub Actions) para calidad de código

**Objetivo:** Automatizar la verificación de estilo, type checking y tests en cada push/PR.

**Pasos:**

1. **Crear workflow básico**

   Archivo sugerido: `.github/workflows/backend-ci.yml` (en el repo raíz), por ejemplo:

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
     test-backend:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.11"

         - name: Install dependencies
           run: |
             cd backend
             pip install -r requirements.txt
             pip install -r requirements-dev.txt

         - name: Lint
           run: |
             cd backend
             ruff check app
             black --check app
             isort --check-only app

         - name: Type check
           run: |
             cd backend
             mypy app

         - name: Tests
           run: |
             cd backend
             pytest --cov=app --cov-report=xml
   ```

2. **Integrar coverage en PR**

   - Opcionalmente usar una acción para comentar cobertura en el PR.
   - O al menos subir `coverage.xml` como artefacto.

3. **Definir políticas de merge**

   - En GitHub, configurar que los PRs al branch principal requieran:
     - CI verde.
     - (Opcional) cobertura mínima.

---

### 3.7. Paso 6 – Aplicar SOLID y clean code de forma incremental

**Objetivo:** Mantener y mejorar la claridad del código a medida que se expande la base de código.

**Pasos concretos:**

1. **Revisar endpoints con más lógica**

   - Identificar en `app/api/v1/endpoints/*` las funciones de endpoint que:
     - Tengan demasiadas validaciones y reglas ad-hoc.
     - Combinen lectura/escritura de DB con lógica de negocio significativa.

2. **Extraer esa lógica a funciones de dominio (servicios)**

   - Crear (si no existe) `app/services/` (ver informe de arquitectura anterior).
   - Por cada endpoint de negocio complejo (`offers`, `bookings`, `payments`):
     - Mover cálculos, cambios de estado, validaciones de negocio a funciones en `services`.
   - Mantener en el endpoint solo:
     - Desempaquetado de request.
     - Orquestación de dependencias (`db`, `current_user`).
     - Llamada a servicio.
     - Construcción de respuesta.

3. **Aplicar “Single Responsibility Principle”**

   - Evitar funciones con más de ~40–50 líneas y más de una razón de cambio.
   - Dividir en helpers si es necesario.

4. **Revisar nombres y parámetros**

   - Asegurarse de que nombres de funciones y variables comuniquen intención:
     - `create_booking_from_offer` es un buen ejemplo.
   - Evitar abreviaturas innecesarias o genéricas (`x`, `data`, `obj`).

---

### 3.8. Paso 7 – Introducir pruebas para lógica crítica (subastas, bookings, pagos)

**Objetivo:** Cubrir primero la lógica de mayor riesgo de negocio.

**Pasos detallados:**

1. **Identificar funciones/módulos de lógica crítica**

   Según `DOCUMENTACION_TECNICA.md` y `PRD_agendamiento.md`:

   - `app/services/bidding.py` (lógica de ofertas, Proxy Bidding, Soft Close).
   - `Booking` + conversión `Offer -> Booking`.
   - `PaymentService` y estado `Transaction`.

2. **Crear tests unitarios para `bidding`**

   - Archivo: `backend/tests/services/test_bidding.py`.
   - Casos mínimos:
     - Primera oferta → se convierte en ganadora, precio actual correcto.
     - Oferta nueva con `max_bid` > actual → ganador cambia y se actualiza precio.
     - Oferta nueva con `max_bid` <= actual → el ganador se mantiene.
     - Soft close: oferta en últimos N minutos extiende `auction_end_time`.

3. **Crear tests de integración para flujo completo**

   - Archivo: `backend/tests/api/v1/test_offers_and_bookings.py`.
   - Flujo:
     1. Crear usuario y login.
     2. Crear máquina y slots (usando endpoints).
     3. Crear oferta ganadora.
     4. Invocar `POST /bookings/from-offer/{offer_id}`.
     5. Verificar que el booking resultante tiene estado `pending_payment`.

4. **Añadir tests para pagos**

   - `backend/tests/api/v1/test_payments.py`.
   - Simulaciones:
     - `create_payment_intent` para booking en `pending_payment`.
     - `confirm_payment` → verifica cambio de estado a `confirmed`.

5. **Medir cobertura y ajustar**

   - Ejecutar `pytest --cov=app`.
   - Revisar qué módulos quedan sin cubrir y decidir prioridades.

---

### 3.9. Paso 8 – Estándar de revisión de código y documentación interna

**Objetivo:** Mantener la calidad cuando se agreguen más desarrolladores / features.

**Pasos:**

1. **Definir guía de estilo interna**

   - Crear `backend/CONTRIBUTING.md` o extender `DOCUMENTACION_TECNICA.md` con:
     - Formato de código: usar black + isort.
     - Linter: ruff.
     - Reglas básicas de mypy.
     - Política de tests: todo cambio debe venir con tests asociados.

2. **Docstrings consistentes**

   - Para funciones de servicios clave:
     - Añadir docstrings con:
       - Propósito.
       - Parámetros.
       - Retorno.
   - Esto ya está comenzado en endpoints; extender a servicios.

3. **Revisión de código obligatoria**

   - Configurar en GitHub:
     - Al menos 1 revisión aprobada antes de merge a main.
   - En la práctica:
     - Revisar estilo, diseño y cobertura de tests, no solo funcionalidad.

---

## Conclusión

La base del backend de CONMAQ es **sana, legible y bien estructurada**, lo que justifica una calificación de **6/10** en Calidad del Código y Mantenibilidad: por encima de lo básico, pero todavía sin el ecosistema de **tests, linters, type checking y CI** requerido para ser considerada “alta calidad” en un entorno productivo exigente.

Siguiendo el plan paso a paso descrito:

1. Fijar dependencias.
2. Introducir estructura y cultura de tests.
3. Integrar linters, formatter y mypy.
4. Configurar CI.
5. Aplicar SOLID y separar lógica de negocio en servicios.
6. Priorizar cobertura en la lógica de mayor riesgo (subastas, bookings, pagos).

se puede evolucionar la calificación hacia **8–9/10**, logrando una base de código:

- Fácil de leer.
- Fácil de modificar sin miedo.
- Lista para escalar en equipo y en funcionalidades.