# Informe de Auditoría – Arquitectura y Diseño de Software (Backend CONMAQ)

## 1. Calificación (Arquitectura y Diseño de Software)

**Calificación global:** **8 / 10**

---

## 2. Explicación de la calificación

### 2.1. Resumen ejecutivo

El backend de CONMAQ presenta una **arquitectura bien planteada**, con una **separación clara de capas**:

- `app/core` – configuración y cross-cutting concerns (limiter, config, seguridad).
- `app/db` – conexión a base de datos y ORM.
- `app/models` – modelos de persistencia (ORM).
- `app/schemas` – DTOs y validación (Pydantic).
- `app/api` – endpoints (controladores) y dependencias (`deps`).
- `backend/DOCUMENTACION_TECNICA.md` – documentación técnica alineada a la arquitectura.
- `backend/PRD_agendamiento.md` y `backend/PLAN_DESARROLLO.md` – diseño y planificación técnica/funcional.

Se sigue claramente un **monolito modular bien estructurado**, alineado con el tamaño actual del proyecto. La API está versionada (`/api/v1`) y las rutas siguen convenciones REST razonables: `/auth`, `/users`, `/machines`, `/offers`, `/watchlist`, `/notifications`, `/bookings`, `/payments`, `/metrics` ([`app/api/v1/api.py`](https://github.com/carlosrueda13/CONMAQ/blob/d8fa2fdb233b387307fdb321b8a6cf6efd47bc7e/backend/app/api/v1/api.py)).

Por estas razones el proyecto encaja sólidamente en la banda **7‑9** de la rúbrica:

> “Arquitectura bien planteada. El sistema está modularizado: controladores (routes), servicios, acceso a datos y modelos están desacoplados. Se siguen patrones de diseño (inyección de dependencias, separación por módulos). La elección entre monolito modular y microservicios se justifica según la escala…”

No se alcanza aún un **10/10** porque:

- No hay un patrón formal como **arquitectura hexagonal o DDD** implementado de forma explícita.
- La capa de “servicios” o “dominio” está **poco explicitada/estandarizada**: mucha lógica de negocio parece residir en los endpoints y modelos en vez de en servicios claramente definidos.
- Falta una estrategia explícita de **bodegas de contexto (bounded contexts)** y modularización interna por dominios (ej. `rentas`, `usuarios`, `pagos`) más allá de la separación por tipo de recurso.
- La parte de **observabilidad, tolerancia a fallos y escalabilidad horizontal** está descrita en el PRD pero aún no se ve operativa/estructurada a nivel de código o módulos (colas, workers, tracing, etc.).  
- Algunos endpoints, como los de **métricas** y **watchlist**, parecen estar implementados directamente sobre ORM + FastAPI sin una capa clara de servicios de dominio, lo que a largo plazo acopla controladores y datos.

### 2.2. Puntos fuertes de la arquitectura actual

1. **Monolito modular claro y razonable**

   - Documentado en `DOCUMENTACION_TECNICA.md`:

     > “El proyecto sigue una arquitectura en capas basada en **FastAPI**, diseñada para separar responsabilidades y facilitar el mantenimiento.  
     > - `app/core`  
     > - `app/db`  
     > - `app/models`  
     > - `app/schemas`  
     > - `app/api`…”

   - Esta estructura es coherente con un **backend CRUD + lógica de negocio moderada** y encaja muy bien en la etapa MVP/Fase 3.
   - Permite entender rápidamente **dónde va cada tipo de código** y reduce el acoplamiento directo entre API y base de datos.

2. **Versionado de API y organización de routers**

   - `app/main.py` define:

     ```python
     app = FastAPI(
         title=settings.PROJECT_NAME,
         openapi_url=f"{settings.API_V1_STR}/openapi.json"
     )
     ```

   - `settings.API_V1_STR = "/api/v1"` en `app/core/config.py`.
   - `app/api/v1/api.py` agrupa routers:

     ```python
     api_router = APIRouter()
     api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
     api_router.include_router(users.router, prefix="/users", tags=["users"])
     api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
     api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
     api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
     api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
     api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
     api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
     api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
     ```

   - Esto ofrece una **API REST versionada y modular**, cumpliendo buenas prácticas de diseño.

3. **Separación clara de modelos de dominio vs. DTOs**

   - `app/models/*` – ORM SQLAlchemy.
   - `app/schemas/*` – Modelos Pydantic, por ejemplo:
     - `app/schemas/user.py`
     - `app/schemas/machine.py`
     - `app/schemas/booking.py`
     - `app/schemas/transaction.py` (documentados en `DOCUMENTACION_TECNICA.md`, sección 6).

   Esta separación permite:

   - Evitar exponer directamente entidades de base de datos.
   - Controlar con precisión qué se recibe y qué se devuelve en la API.
   - Evolucionar el esquema externo sin necesariamente cambiar el modelo interno inmediatamente.

4. **Uso sistemático de dependencias de FastAPI (inyección de dependencias)**

   - `app/api/deps.py` concentra funciones de dependencia:

     - `get_db`
     - `get_current_user`
     - `get_current_active_user`
     - `get_current_active_superuser`
     - `get_current_active_admin`

   - Los endpoints las reutilizan, por ejemplo en `notifications.py`:

     ```python
     @router.get("/", response_model=List[NotificationSchema])
     def read_notifications(
         db: Session = Depends(deps.get_db),
         skip: int = 0,
         limit: int = 100,
         current_user: User = Depends(deps.get_current_active_user),
     ) -> Any:
         ...
     ```

   - En `metrics.py`:

     ```python
     @router.get("/financial")
     def get_financial_metrics(
         db: Session = Depends(deps.get_db),
         current_user: Any = Depends(deps.get_current_active_admin),
     ):
         ...
     ```

   Esto demuestra un buen uso de:

   - **Inyección de dependencias** para base de datos.
   - **Seguridad transversal** (auth, roles) desacoplada de los controladores.

5. **Rutas bastante RESTful y consistentes**

   - `users`: `POST /users`, `GET /users/me`
   - `watchlist`: `POST /watchlist/toggle`, `GET /watchlist/`
   - `notifications`: `GET /notifications/`, `PUT /notifications/{id}/read`
   - `bookings`: endpoints bien documentados en `DOCUMENTACION_TECNICA.md` (`create_booking_from_offer`, `check_in`, `check_out`, `call_off`).
   - `metrics`: agrupado en `/metrics/financial`, `/metrics/machines`.

   Aunque hay algunos endpoints “acción” (ej: `toggle`, `check_in`, `call_off`), están contenidos y razonablemente nombrados. En general, la API es:

   - Intuitiva.
   - Coherente en prefijos y tags.
   - Fácil de evolucionar hacia más recursos o sub-recursos.

6. **Consideraciones de cross-cutting concerns y escalabilidad**

   - **Rate limiting** con `slowapi` (`app.core.limiter`, uso en `users.py`):

     ```python
     @router.post("/", response_model=UserSchema)
     @limiter.limit("5/minute")
     def create_user(...):
         ...
     ```

   - **CORS y TrustedHost** en `main.py`.
   - Configuración pensada para despliegue con Docker / Kubernetes (`PLAN_DESARROLLO.md`, `PRD_agendamiento.md`).
   - PRD menciona:
     - Redis como cache/queue.
     - Celery para workers.
     - Observabilidad (Prometheus, OpenTelemetry).
   - Aunque no todos estos componentes están aún implementados, la **arquitectura se ha diseñado pensando en ellos**, lo que facilita el salto a un sistema más distribuido.

### 2.3. Principales puntos de mejora detectados

1. **Lógica de negocio mezclada en endpoints**

   - Por los fragmentos y por la documentación técnica, se infiere que mucha lógica de negocio está en los ficheros de endpoints (`app/api/v1/endpoints/*.py`) y en los modelos, en vez de estar en una capa de **servicios de dominio**.
   - Esto hace que:
     - Los controladores hagan “demasiadas cosas”: validan, orquestan, calculan reglas de negocio y llaman al ORM.
     - La reusabilidad y testeo unitario de las reglas de negocio sea más difícil.

2. **Ausencia de una capa de servicios/módulo de dominio explícito**

   - No se ve un directorio tipo `app/services` o `app/domain`.
   - La lógica para:
     - creación de bookings a partir de ofertas,
     - validaciones de solapamientos,
     - lógica de métricas financieras y de máquinas,
     - estados de notificaciones y watchlist,
     aparenta estar en los controladores o en las entidades ORM.
   - Esto impide llegar a un diseño tipo **arquitectura hexagonal** o **DDD light**, que permitiría:
     - Desacoplar completamente API, dominio y persistencia.
     - Reusar el dominio en otros interfaces (por ejemplo, workers Celery o CLI de administración).

3. **Modularización por dominio solo parcial**

   - Actualmente la modularización se hace **por tipo de recurso** (`machines`, `offers`, `bookings`, etc.) pero no hay una capa intermedia que agrupe:
     - Dominios como “Subastas y Ofertas”, “Rentas y Calendarios”, “Pagos”.
   - A medida que crezca el proyecto, los endpoints podrían volverse muy grandes porque cada archivo de endpoints termina gestionando muchos casos de uso.

4. **REST avanzado y recursos de acciones**

   - Endpoints como:
     - `POST /watchlist/toggle`
     - `PUT /notifications/{id}/read`
     - `POST /bookings/{id}/check_in`
     - `POST /bookings/{id}/call_off`
   - Aunque son prácticos, representan acciones sobre recursos que podrían beneficiarse de:
     - Una convención más RESTful (ej: `/bookings/{id}/status` con PATCH y body).
     - O una especificación más clara y homogénea de acciones (usar siempre `POST /{resource}/{id}/{action}` para comandos).

5. **Arquitectura avanzada (Hexagonal/DDD) no formalizada**

   - El proyecto **apunta** a buenas prácticas (monolito modular, capas claras), pero no se ve:
     - Un puerto/adaptador explícito.
     - Un layer de dominio independiente de FastAPI y SQLAlchemy.
     - Interfaces para los servicios de infraestructura (pagos, notificaciones externas, colas).
   - Para llegar a un **10/10**, faltaría formalizar esta separación y documentarla (ej. en `DOCUMENTACION_TECNICA.md` explicar puertos, adaptadores y contexto de dominios).

---

## 3. Plan detallado de mejoras y correcciones  
*(Estilo “manual de LEGO”: pasos concretos, en orden sugerido)*

### 3.1. Objetivos del plan

1. **Consolidar el monolito modular** actual para que escale en complejidad sin volverse espagueti.
2. **Extraer y aislar la lógica de negocio** de los endpoints a una capa de servicios.
3. **Preparar el terreno para una arquitectura hexagonal / DDD light** sin reescribir todo.
4. **Refinar la API REST** para mantener coherencia al agregar nuevas operaciones.
5. **Dejar lista la base** para añadir workers, colas y observabilidad sin romper la arquitectura.

---

### 3.2. Paso 1 – Introducir una capa de servicios de dominio

**Objetivo:** Crear un lugar claro para la lógica de negocio, separándola de los controladores FastAPI y del ORM.

**Pasos (LEGO):**

1. **Crear un nuevo paquete `app/services`**

   - Estructura inicial propuesta:

     ```
     app/
       services/
         __init__.py
         users.py
         machines.py
         offers.py
         bookings.py
         payments.py
         notifications.py
         watchlist.py
         metrics.py
     ```

2. **Definir servicios por dominio**

   Para cada archivo de endpoints en `app/api/v1/endpoints/`:

   - `users.py` → `app/services/users.py`
   - `machines.py` → `app/services/machines.py`
   - `offers.py` → `app/services/offers.py`
   - `bookings.py` → `app/services/bookings.py`
   - `payments.py` → `app/services/payments.py`
   - `notifications.py` → `app/services/notifications.py`
   - `watchlist.py` → `app/services/watchlist.py`
   - `metrics.py` → `app/services/metrics.py`

   En cada archivo de servicio:

   - Definir funciones claras que implementen **casos de uso**.  
   - Ejemplo para watchlist:

     ```python
     # app/services/watchlist.py
     from sqlalchemy.orm import Session
     from app.models.user import User
     from app.models.watchlist import Watchlist
     from app.schemas.watchlist import WatchlistCreate

     def toggle_watchlist_for_user(
         db: Session, current_user: User, watchlist_in: WatchlistCreate
     ):
         # aquí iría la lógica de toggle que hoy está en el endpoint
         ...
     ```

3. **Refactorizar endpoints para que solo orquesten**

   - `app/api/v1/endpoints/watchlist.py` antes:

     ```python
     @router.post("/toggle", response_model=Any)
     def toggle_watchlist(
         *,
         db: Session = Depends(deps.get_db),
         watchlist_in: WatchlistCreate,
         current_user: User = Depends(deps.get_current_active_user),
     ) -> Any:
         """
         Toggle a machine in the user's watchlist.
         """
         # lógica de toggle aquí (posiblemente)
     ```

   - Después:

     ```python
     from app.services.watchlist import toggle_watchlist_for_user

     @router.post("/toggle", response_model=Any)
     def toggle_watchlist(
         *,
         db: Session = Depends(deps.get_db),
         watchlist_in: WatchlistCreate,
         current_user: User = Depends(deps.get_current_active_user),
     ) -> Any:
         return toggle_watchlist_for_user(db, current_user, watchlist_in)
     ```

   - Hacer lo mismo en:
     - `notifications.read_notifications` → `services.notifications.get_user_notifications`.
     - `notifications.mark_notification_as_read` → `services.notifications.mark_as_read`.
     - `metrics.get_financial_metrics` → `services.metrics.get_financial_metrics`.
     - `metrics.get_machine_metrics` → `services.metrics.get_machine_metrics`.
     - `bookings.check_in`, `check_out`, `call_off` → funciones en `services.bookings`.

4. **Beneficio inmediato:**

   - Los servicios se pueden testear sin levantar FastAPI.
   - Los endpoints se vuelven delgados y declarativos.

---

### 3.3. Paso 2 – Estandarizar patrones de entrada/salida en servicios

**Objetivo:** Que los servicios sean fácilmente reutilizables y consistentes.

**Pasos:**

1. **Decidir contrato de los servicios**

   - Servicios reciben:
     - `db: Session`
     - `actor` o `current_user` (cuando aplique).
     - DTOs de entrada (`schemas`).
   - Servicios devuelven:
     - Entidades de dominio (modelos ORM) o DTOs de salida (`schemas`).

   Ejemplo para notificaciones:

   ```python
   # app/services/notifications.py
   from typing import List
   from sqlalchemy.orm import Session
   from app.models.user import User
   from app.models.notification import Notification

   def get_user_notifications(
       db: Session, current_user: User, skip: int = 0, limit: int = 100
   ) -> List[Notification]:
       ...
   ```

2. **Evitar `HTTPException` dentro de servicios**

   - Validaciones de negocio deben lanzar **excepciones de dominio** (custom) o devolver resultados explícitos (ej. `None`, `Result`).
   - Los endpoints convierten esas excepciones a `HTTPException`.
   - Esto desacopla la lógica de negocio del protocolo HTTP.

3. **Documentar este patrón en `DOCUMENTACION_TECNICA.md`**

   - Añadir una subsección “Capa de Servicios” explicando:
     - Qué es un servicio.
     - Convenciones de firma y retorno.
     - Regla: “Sin `HTTPException` en servicios”.

---

### 3.4. Paso 3 – Modularizar por dominio (submódulos de servicios)

**Objetivo:** Evitar que `services` se convierta en una carpeta gigante desordenada.

**Pasos:**

1. **Reorganizar `app/services` por dominios más ricos**

   Ejemplo de estructura:

   ```
   app/services/
     users/
       __init__.py
       commands.py   # create_user, update_user_profile...
       queries.py    # get_user_by_id, search_users...
     rentals/
       __init__.py
       bookings.py   # create_booking, check_in, check_out...
       calendar.py   # slots y disponibilidad
       offers.py     # lógica de subastas/ofertas
     machines/
       __init__.py
       machines.py   # CRUD y lógica de estado de máquinas
     payments/
       __init__.py
       stripe_adapter.py (o el proveedor)
       transactions.py
     notifications/
       __init__.py
       notifications.py
     analytics/
       __init__.py
       metrics.py
   ```

2. **Actualizar imports en endpoints**

   - Ejemplo: bookings:

     ```python
     # app/api/v1/endpoints/bookings.py
     from app.services.rentals.bookings import create_booking_from_offer_service
     ```

3. **Al documentar en `DOCUMENTACION_TECNICA.md`**, incluir un diagrama simple tipo:

   - `API (FastAPI)` → llama a → `Servicios de Dominio` → utilizan → `Modelos (ORM)` + `Infraestructura (pagos, colas, etc.)`.

---

### 3.5. Paso 4 – Preparar una “arquitectura hexagonal light”

**Objetivo:** Sin reescribir el proyecto, acercarse a una arquitectura hexagonal / DDD que permita:

- Sustituir fácilmente proveedores externos (Stripe, SendGrid, Redis).
- Reutilizar el dominio en otros canales (workers, CLI, etc.).

**Pasos:**

1. **Definir interfaces (puertos) para infraestructura**

   Crear un módulo `app/core/ports`:

   ```
   app/core/ports/
     __init__.py
     payments.py       # interface PaymentGateway
     notifications.py  # interface NotificationSender
     storage.py        # para fotos, etc.
   ```

   Ejemplo de puerto:

   ```python
   # app/core/ports/payments.py
   from abc import ABC, abstractmethod
   from typing import Protocol

   class PaymentGateway(Protocol):
       def charge(self, amount: float, currency: str, source: str) -> str:
           """Realiza un cargo y retorna un id de transacción."""
   ```

2. **Crear adaptadores concretos en `app/infrastructure`**

   ```
   app/infrastructure/
     payments/
       __init__.py
       stripe_gateway.py
     notifications/
       __init__.py
       sendgrid_sender.py
   ```

3. **Hacer que los servicios dependan de puertos, no de implementaciones**

   - En `services/payments.py`, recibir un `PaymentGateway` como parámetro (inyectado via dependencia o fábrica).
   - Esto facilita testear con mocks/fakes.

4. **Documentar en `DOCUMENTACION_TECNICA.md`**

   - Añadir sección: “Arquitectura: Puertos y Adaptadores”.
   - Explicar cómo API / workers usan los **mismos servicios** de dominio, que a su vez llaman a puertos implementados por adaptadores concretos.

---

### 3.6. Paso 5 – Revisión y refinamiento de la API REST

**Objetivo:** Homogeneizar patrones REST de rutas y acciones.

**Pasos prácticos:**

1. **Definir convención de acciones sobre recursos**

   Decide una de estas dos aproximaciones y documentarla:

   - **Opción A (REST puro + estados):**
     - Acciones se representan como cambios de **estado** en recursos.
     - Ejemplo: `check_in` y `check_out` se modelan como cambios en un campo `status` del booking mediante:
       - `PATCH /bookings/{id}` con un body `{ "status": "checked_in" }`.

   - **Opción B (comandos explícitos con sub-ruta):**
     - Acciones son sub-recursos de comando:
       - `POST /bookings/{id}/check_in`
       - `POST /bookings/{id}/check_out`
       - `POST /bookings/{id}/call_off`

   Cualquiera de las dos es válida, pero **debe ser consistente** en toda la API.

2. **Revisar endpoints “toggle”**

   - `POST /watchlist/toggle` podría alternarse a:
     - `PUT /watchlist/{machine_id}` para “añadir”.
     - `DELETE /watchlist/{machine_id}` para “remover”.
   - O mantener `toggle`, pero dejarlo documentado como endpoint de “comando” fuera del CRUD puro.

3. **Documentar las decisiones**

   - Añadir a `DOCUMENTACION_TECNICA.md` una tabla de “Convenciones de Rutas y Métodos HTTP”.
   - Ejemplo de entradas:
     - `GET /{resource}` – listar.
     - `GET /{resource}/{id}` – detalle.
     - `POST /{resource}` – crear.
     - `PUT/PATCH /{resource}/{id}` – actualizar.
     - `DELETE /{resource}/{id}` – eliminar.
     - `POST /{resource}/{id}/{action}` – comando específico (si se adopta Opción B).

---

### 3.7. Paso 6 – Delimitar bounded contexts ligeros

**Objetivo:** Preparar el camino para eventualmente separar dominios en microservicios sin reescritura masiva.

**Pasos:**

1. **Identificar dominios principales (ya casi están definidos en el PRD)**

   - **Usuarios y Autenticación**
   - **Catálogo de Máquinas**
   - **Ofertas y Subastas**
   - **Bookings y Calendario**
   - **Pagos y Finanzas**
   - **Notificaciones y Comunicación**
   - **Métricas y Analítica**

2. **Mapear cada dominio a:**

   - Servicios (`app/services/<dominio>`)
   - Modelos (`app/models/*` relacionados)
   - Esquemas (`app/schemas/*` relacionados)
   - Routers (`app/api/v1/endpoints/*` relacionados)

3. **Crear una tabla en `DOCUMENTACION_TECNICA.md`**

   Algo como:

   | Dominio              | Routers                   | Servicios                          | Modelos principales            |
   |----------------------|---------------------------|------------------------------------|--------------------------------|
   | Usuarios/Auth        | `auth.py`, `users.py`     | `services.users.*`                 | `User`                         |
   | Máquinas             | `machines.py`             | `services.machines.*`              | `Machine`                      |
   | Ofertas/Subastas     | `offers.py`               | `services.rentals.offers`         | `Offer`                        |
   | Bookings/Calendario  | `bookings.py`             | `services.rentals.bookings`       | `Booking`, `AvailabilitySlot` |
   | Pagos                | `payments.py`             | `services.payments.*`             | `Transaction`                  |
   | Notificaciones       | `notifications.py`        | `services.notifications.*`        | `Notification`                 |
   | Watchlist            | `watchlist.py`            | `services.watchlist.*`            | `Watchlist`                    |
   | Métricas/Analytics   | `metrics.py`              | `services.analytics.metrics`      | (usa varias tablas)           |

4. **Beneficio**

   - Si en el futuro se quiere extraer, por ejemplo, **Pagos** a un microservicio, ya hay un **bounded context** conceptual y técnico donde reside la lógica.

---

### 3.8. Paso 7 – Observabilidad, escalabilidad y resiliencia alineadas a la arquitectura

**Objetivo:** Conectar lo definido en el PRD con la implementación real, sin romper el diseño.

**Pasos:**

1. **Crear módulos de observabilidad en `app/core`**

   - `app/core/logging.py` – configuración de logs estructurados.
   - `app/core/metrics.py` – helpers para Prometheus (si se usa).
   - `app/core/tracing.py` – inicialización de OpenTelemetry.

2. **Integrar en `app/main.py`**

   - Inicializar logging, metrics y tracing al arrancar la app.
   - Asegurarse que estas capas son **puramente transversales** y no se mezclan con lógica de negocio ni endpoints.

3. **Workers y colas**

   - Crear un módulo `app/workers/` donde se usen los **mismos servicios de dominio** (`app/services/*`) para ejecutar tareas en background (subastas, notificaciones, etc.).
   - Workers usan:
     - Puertos/adaptadores (`app/core/ports`, `app/infrastructure`) para pagos, emails, etc.
     - Nunca acceden directamente a endpoints.

4. **Documentar el flujo**

   - En `DOCUMENTACION_TECNICA.md`, agregar un diagrama de alto nivel:
     - Cliente HTTP → FastAPI → Servicios → Modelos/Infra.
     - Worker → Servicios → Modelos/Infra.
     - Métricas/Logs/Tracing como capa envolvente.

---

### 3.9. Paso 8 – Checklist final para acercarse al 10/10

Para aproximar la calificación **10** de la rúbrica:

1. **Arquitectura Hexagonal Light completada**

   - Servicios de dominio sin dependencias fuertes a FastAPI/HTTP.
   - Uso de puertos/adaptadores para infraestructura clave.

2. **Bounded contexts claros y documentados**

   - Tabla de dominios + módulos, como se describió en el Paso 6.

3. **API REST coherente y versionada**

   - Rutas consistentes.
   - Convención documentada para acciones sobre recursos.
   - Documentación de endpoints actualizada y exportable (OpenAPI, etc.).

4. **Estrategia de escalabilidad y tolerancia a fallos operativa**

   - Rate limiters y CORS ya están bien encaminados.
   - Faltaría:
     - Integración real de Redis/colas.
     - Workers independientes que usan servicios de dominio.
     - Estrategia de reintentos y manejo de fallos en pagos/notificaciones.

5. **Documentación alineada con la implementación**

   - `DOCUMENTACION_TECNICA.md` ya es muy buena base.
   - Actualizarla tras cada refactor clave para mantenerla confiable como “verdad arquitectónica”.

---

## Conclusión

El backend de CONMAQ está **muy bien encaminado arquitectónicamente**, con un monolito modular, separación de capas, uso adecuado de FastAPI, Pydantic y SQLAlchemy, y una documentación técnica sobresaliente. La calificación **8/10** refleja una arquitectura madura para un MVP serio, con margen de mejora principalmente en:

- Formalizar capa de servicios de dominio.
- Introducir puertos/adaptadores.
- Modularizar por dominios (bounded contexts ligeros).
- Afinar algunos detalles REST y operativos.

Siguiendo el plan detallado anterior, se puede evolucionar gradualmente hacia una arquitectura cercana a **hexagonal/DDD**, apta para altas exigencias de escalabilidad y mantenimiento, sin necesidad de reescribir el sistema desde cero.