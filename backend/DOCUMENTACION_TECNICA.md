# Manual Técnico de Referencia - Sistema CONMAQ

**Versión del Documento:** 1.2
**Fecha de Última Actualización:** 25 de Noviembre de 2025
**Estado:** Fase 2 (Motor de Subastas y Notificaciones)

---

## Tabla de Contenidos
1. [Introducción](#1-introducción)
2. [Arquitectura del Proyecto](#2-arquitectura-del-proyecto)
3. [Configuración y Entorno](#3-configuración-y-entorno)
4. [Módulo Core (Núcleo)](#4-módulo-core-núcleo)
5. [Capa de Datos (Modelos y DB)](#5-capa-de-datos-modelos-y-db)
6. [Capa de Esquemas (DTOs)](#6-capa-de-esquemas-dtos)
7. [Capa de API y Controladores](#7-capa-de-api-y-controladores)
8. [Seguridad e Inyección de Dependencias](#8-seguridad-e-inyección-de-dependencias)
9. [Utilidades de Negocio](#9-utilidades-de-negocio)
10. [Testing y Despliegue](#10-testing-y-despliegue)

---

## 1. Introducción

Este documento sirve como la referencia técnica definitiva para el backend del sistema CONMAQ. Está diseñado para proporcionar a los desarrolladores una comprensión profunda de cada componente, función y variable dentro del código base. A diferencia de un informe de progreso, este manual detalla el **cómo** y el **por qué** de la implementación actual.

---

## 2. Arquitectura del Proyecto

El proyecto sigue una arquitectura en capas basada en **FastAPI**, diseñada para separar responsabilidades y facilitar el mantenimiento.

### Estructura de Directorios
- **`app/core`**: Contiene la configuración global y lógica de seguridad transversal.
- **`app/db`**: Maneja la conexión a la base de datos y la definición del ORM.
- **`app/models`**: Define las tablas de la base de datos (Entidades).
- **`app/schemas`**: Define los modelos Pydantic para validación de datos (Data Transfer Objects).
- **`app/api`**: Contiene los endpoints (controladores) y dependencias.

---

## 3. Configuración y Entorno

La configuración se gestiona mediante la librería `pydantic-settings`, que lee variables de entorno y las valida contra tipos de datos estrictos.

### Archivo: `app/core/config.py`

#### Clase `Settings`
Esta clase singleton almacena toda la configuración de la aplicación.

**Atributos (Variables de Entorno):**

| Nombre Variable | Tipo | Descripción | Valor por Defecto |
| :--- | :--- | :--- | :--- |
| `PROJECT_NAME` | `str` | Nombre público de la aplicación. | "Agendamiento API" |
| `API_V1_STR` | `str` | Prefijo para versionado de rutas. | "/api/v1" |
| `POSTGRES_SERVER` | `str` | Hostname del servidor de base de datos. | "db" |
| `POSTGRES_USER` | `str` | Usuario para autenticación en PostgreSQL. | "postgres" |
| `POSTGRES_PASSWORD` | `str` | Contraseña del usuario de PostgreSQL. | "postgres" |
| `POSTGRES_DB` | `str` | Nombre de la base de datos lógica. | "agendamiento" |
| `POSTGRES_PORT` | `str` | Puerto del servidor de base de datos. | "5432" |
| `DATABASE_URL` | `Optional[str]` | URI de conexión completa (SQLAlchemy). | *Calculado automáticamente* |
| `SECRET_KEY` | `str` | Clave criptográfica para firmar JWTs. **CRÍTICO**. | "changethis..." (Dev) |
| `ALGORITHM` | `str` | Algoritmo de firma para JWT. | "HS256" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | Tiempo de vida del token en minutos. | 30 |

**Métodos:**

- **`__init__(self, **kwargs)`**:
    - **Propósito:** Constructor que inicializa la configuración.
    - **Lógica:** Si `DATABASE_URL` no se provee explícitamente en el entorno, la construye dinámicamente concatenando `postgresql://` + usuario + password + servidor + db.

---

## 4. Módulo Core (Núcleo)

### Archivo: `app/core/security.py`

Este módulo encapsula la criptografía y manejo de tokens.

#### Variable: `pwd_context`
- **Tipo:** `CryptContext` (Passlib)
- **Configuración:** Esquema `bcrypt`, deprecación automática.
- **Uso:** Motor principal para hashear y verificar contraseñas.

#### Función: `create_access_token`
Genera un JSON Web Token (JWT) firmado.

```python
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str
```

- **Parámetros:**
    - `subject` (`Union[str, Any]`): El identificador principal del usuario (usualmente `user.id`) que será el "subject" (`sub`) del token.
    - `expires_delta` (`timedelta`, opcional): Tiempo personalizado de expiración. Si es `None`, usa `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **Retorno:** `str` (El token JWT codificado).
- **Lógica:**
    1. Calcula la fecha `exp` (UTC actual + delta).
    2. Crea un diccionario `to_encode` con `exp` y `sub`.
    3. Codifica el diccionario usando `jwt.encode` con la `SECRET_KEY` y el `ALGORITHM`.

#### Función: `verify_password`
Verifica si una contraseña en texto plano coincide con su hash.

```python
def verify_password(plain_password: str, hashed_password: str) -> bool
```

- **Parámetros:**
    - `plain_password` (`str`): Contraseña ingresada por el usuario.
    - `hashed_password` (`str`): Hash almacenado en la base de datos.
- **Retorno:** `bool` (`True` si coinciden, `False` si no).

#### Función: `get_password_hash`
Convierte una contraseña plana en un hash seguro.

```python
def get_password_hash(password: str) -> str
```

- **Parámetros:** `password` (`str`).
- **Retorno:** `str` (Hash Bcrypt).

---

## 5. Capa de Datos (Modelos y DB)

### Archivo: `app/db/session.py`

- **`engine`**: Instancia de `sqlalchemy.create_engine`. Maneja el pool de conexiones a PostgreSQL. Configurado con `pool_pre_ping=True` para evitar errores de desconexión.
- **`SessionLocal`**: Fábrica de sesiones (`sessionmaker`). Cada request HTTP instanciará una sesión propia usando esta fábrica. Configuración: `autocommit=False`, `autoflush=False`.

### Archivo: `app/models/user.py`

#### Clase `User` (Hereda de `Base`)
Representa la tabla `user` en la base de datos.

**Columnas:**

| Nombre | Tipo SQLAlchemy | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | `primary_key=True`, `index=True` | Identificador único auto-incremental. |
| `email` | `String` | `unique=True`, `index=True`, `nullable=False` | Correo electrónico (username). |
| `hashed_password` | `String` | `nullable=False` | Hash de la contraseña. |
| `full_name` | `String` | `index=True` | Nombre completo del usuario. |
| `phone` | `String` | - | Teléfono de contacto. |
| `role` | `String` | `default="client"` | Rol RBAC (client, admin, operator). |
| `is_active` | `Boolean` | `default=True` | Soft-delete. Si es False, no puede loguearse. |
| `is_superuser` | `Boolean` | `default=False` | Permisos totales de administración. |
| `created_at` | `DateTime` | `server_default=func.now()` | Timestamp de creación. |

#### Clase `Machine` (Hereda de `Base`)
Representa la maquinaria disponible para renta.

**Columnas Principales:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `name` | `String` | Nombre comercial de la máquina. |
| `serial_number` | `String` | Número de serie único. `unique=True`, `nullable=False`. |
| `specs` | `JSON` | Diccionario flexible para especificaciones técnicas. |
| `price_base_per_hour` | `Float` | Tarifa base por hora. |
| `location_lat/lng` | `Float` | Coordenadas geográficas. |
| `status` | `String` | Estado (available, maintenance, rented). |

#### Clase `AvailabilitySlot` (Hereda de `Base`)
Representa una franja horaria específica de disponibilidad.

**Columnas:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `machine_id` | `Integer` | FK a `machine.id`. |
| `start_time` | `DateTime` | Inicio del slot. |
| `end_time` | `DateTime` | Fin del slot. |
| `is_available` | `Boolean` | Si está libre para ser reservado. |
| `current_price` | `Float` | Precio actual de la subasta (highest bid). |
| `winner_id` | `Integer` | FK a `user.id`. Usuario que va ganando. |
| `auction_end_time` | `DateTime` | Hora de cierre de la subasta (dinámica). |

#### Clase `Offer` (Hereda de `Base`)
Representa una oferta realizada por un usuario en un slot.

**Columnas:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `user_id` | `Integer` | FK a `user.id`. |
| `slot_id` | `Integer` | FK a `availabilityslot.id`. |
| `amount` | `Float` | Monto visible de la oferta. |
| `max_bid` | `Float` | Monto máximo secreto (Proxy Bidding). |
| `status` | `String` | Estado (`active`, `winning`, `outbid`). |

#### Clase `Watchlist` (Hereda de `Base`)
Representa el interés de un usuario en una máquina específica.

**Columnas:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `user_id` | `Integer` | FK a `user.id`. |
| `machine_id` | `Integer` | FK a `machine.id`. |
| `created_at` | `DateTime` | Fecha de adición. |

**Restricciones:**
- `UniqueConstraint('user_id', 'machine_id')`: Evita duplicados.

#### Clase `Notification` (Hereda de `Base`)
Almacena alertas y mensajes para el usuario.

**Columnas:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `user_id` | `Integer` | FK a `user.id`. |
| `type` | `String` | Tipo de evento (`outbid`, `won`, `availability`). |
| `title` | `String` | Título corto. |
| `message` | `String` | Cuerpo del mensaje. |
| `payload` | `JSON` | Datos extra para navegación (ej. `slot_id`). |
| `is_read` | `Boolean` | Estado de lectura. |

---

## 6. Capa de Esquemas (DTOs)

Ubicación: `app/schemas/`. Usamos Pydantic para validación de entrada/salida.

### Archivo: `app/schemas/user.py`

#### Clase `UserBase`
Propiedades compartidas visibles.
- `email`: `EmailStr` (Valida formato de correo).
- `is_active`: `bool`.
- `full_name`: `str`.

#### Clase `UserCreate` (Input)
Usada en el registro (`POST /users/`).
- Hereda de `UserBase`.
- **Requeridos:** `email`, `password` (texto plano).

#### Clase `User` (Output)
Usada para responder al cliente.
- Hereda de `UserInDBBase`.
- **Importante:** No incluye el campo `password`.

### Archivo: `app/schemas/token.py`

#### Clase `Token`
Respuesta del endpoint de login.
- `access_token`: `str`.
- `token_type`: `str` (siempre "bearer").

### Archivo: `app/schemas/machine.py`
DTOs para gestión de máquinas.
- `MachineCreate`: Validación al crear. Campos obligatorios como `name`, `serial_number`, `price_base_per_hour`.
- `MachineUpdate`: Todos los campos opcionales.
- `Machine`: Respuesta completa incluyendo `id` y `created_at`.

### Archivo: `app/schemas/availability.py`
DTOs para disponibilidad.
- `AvailabilitySlot`: Representación de un slot con `start_time`, `end_time`, `is_available`.

### Archivo: `app/schemas/offer.py`
DTOs para gestión de ofertas.
- `OfferCreate`: Input para crear oferta.
    - `amount`: `float` (Requerido). El monto de la oferta visible.
    - `max_bid`: `Optional[float]`. El monto máximo para Proxy Bidding. Si se omite, se asume igual a `amount` (Oferta Manual).
- `Offer`: Output con detalles completos (`status`, `created_at`).

### Archivo: `app/schemas/watchlist.py`
DTOs para lista de seguimiento.
- `WatchlistCreate`: Input vacío (el ID viene en la URL o payload simple).
- `Watchlist`: Output con `machine_id` y `created_at`.

### Archivo: `app/schemas/notification.py`
DTOs para notificaciones.
- `Notification`: Output completo incluyendo `payload` y `is_read`.

---

## 7. Capa de API y Controladores

### Archivo: `app/api/v1/endpoints/auth.py`

#### Endpoint: `login_access_token`
- **Ruta:** `POST /api/v1/auth/login/access-token`
- **Input:** `OAuth2PasswordRequestForm` (username, password).
- **Output:** `Token` schema.
- **Lógica:**
    1. Busca usuario por email (`username`).
    2. Verifica password con `security.verify_password`.
    3. Verifica si `user.is_active`.
    4. Genera token con `security.create_access_token`.
    5. Retorna token.
- **Errores:** Retorna 400 si credenciales son inválidas o usuario inactivo.

### Archivo: `app/api/v1/endpoints/users.py`

#### Endpoint: `create_user`
- **Ruta:** `POST /api/v1/users/`
- **Input:** `UserCreate` (JSON).
- **Output:** `User` (JSON sin password).
- **Lógica:**
    1. Verifica si el email ya existe en DB. Si sí, lanza 400.
    2. Crea instancia del modelo `User`.
    3. Hashea el password.
    4. Guarda en DB (`db.add`, `db.commit`).
    5. Retorna el objeto creado.

#### Endpoint: `read_user_me`
- **Ruta:** `GET /api/v1/users/me`
- **Dependencia:** `get_current_active_user`.
- **Lógica:** Retorna el objeto usuario asociado al token actual.

### Archivo: `app/api/v1/endpoints/machines.py`

#### Endpoint: `read_machines`
- **Ruta:** `GET /api/v1/machines/`
- **Filtros:** `status`, `serial_number`.
- **Lógica:** Retorna la lista de máquinas, opcionalmente filtrada.

#### Endpoint: `create_machine`
- **Ruta:** `POST /api/v1/machines/`
- **Permisos:** Solo Superusuario.
- **Lógica:** Crea una nueva máquina en el sistema.

#### Endpoint: `generate_machine_availability`
- **Ruta:** `POST /api/v1/machines/{id}/availability/generate`
- **Parámetros:** `days` (default 30), `start_hour` (default 8), `end_hour` (default 18).
- **Lógica:** Invoca al `scheduler` para crear slots de disponibilidad.

#### Endpoint: `read_machine_availability`
- **Ruta:** `GET /api/v1/machines/{id}/availability`
- **Filtros:** `start_date`, `end_date`.
- **Lógica:** Retorna la lista de slots para una máquina.

### Archivo: `app/api/v1/endpoints/offers.py`

#### Endpoint: `create_offer`
- **Ruta:** `POST /api/v1/offers/`
- **Input:** `OfferCreate` (`slot_id`, `amount`, `max_bid` opcional).
- **Lógica:** Invoca `bidding.place_bid`. Soporta dos modos:
    1. **Proxy Bidding:** Si se envía `max_bid`, el sistema oferta automáticamente hasta ese límite.
    2. **Manual Bidding:** Si no se envía `max_bid`, la oferta es fija por el valor de `amount`.

#### Endpoint: `read_my_offers`
- **Ruta:** `GET /api/v1/offers/my-offers`
- **Lógica:** Retorna el historial de ofertas del usuario autenticado.

### Archivo: `app/api/v1/endpoints/watchlist.py`

#### Endpoint: `toggle_watchlist`
- **Ruta:** `POST /api/v1/watchlist/toggle`
- **Input:** `WatchlistCreate` (`machine_id`).
- **Lógica:**
    1. Busca si ya existe la relación `user_id` - `machine_id`.
    2. Si existe: Elimina el registro (Remove).
    3. Si no existe: Crea el registro (Add).
    4. Retorna estado (`added` o `removed`).

#### Endpoint: `read_watchlist`
- **Ruta:** `GET /api/v1/watchlist/`
- **Lógica:** Retorna todas las máquinas seguidas por el usuario.

### Archivo: `app/api/v1/endpoints/notifications.py`

#### Endpoint: `read_notifications`
- **Ruta:** `GET /api/v1/notifications/`
- **Lógica:** Retorna notificaciones del usuario, ordenadas por fecha descendente.

#### Endpoint: `mark_notification_as_read`
- **Ruta:** `PUT /api/v1/notifications/{id}/read`
- **Lógica:** Actualiza el campo `is_read = True` para la notificación especificada.

---

## 8. Seguridad e Inyección de Dependencias

### Archivo: `app/api/deps.py`

Este archivo contiene las funciones "Dependency" de FastAPI que se ejecutan antes de los controladores.

#### Función: `get_db`
Generador de sesiones de base de datos.
- **Uso:** `db: Session = Depends(get_db)`
- **Comportamiento:**
    1. Crea `SessionLocal()`.
    2. Entrega la sesión al endpoint (`yield`).
    3. Asegura que `db.close()` se llame al finalizar el request (bloque `finally`), previniendo fugas de conexión.

#### Variable: `reusable_oauth2`
Instancia de `OAuth2PasswordBearer`.
- Define que el cliente debe enviar el token en el header `Authorization: Bearer <token>`.
- Apunta a la URL de login para documentación Swagger.

#### Función: `get_current_user`
Autenticación principal.
- **Parámetros:** `token` (extraído automáticamente del header).
- **Lógica:**
    1. Decodifica el token JWT usando `settings.SECRET_KEY`.
    2. Valida que el payload tenga un `sub` (subject).
    3. Busca al usuario en la DB usando ese ID.
    4. Si no existe o token inválido, lanza `HTTPException 403` o `404`.
- **Retorno:** Instancia del modelo `User`.

#### Función: `get_current_active_user`
Validación de estado.
- **Dependencia:** Llama a `get_current_user`.
- **Lógica:** Verifica `user.is_active`. Si es falso, lanza 400.

---

## 9. Utilidades de Negocio

### Archivo: `app/utils/scheduler.py`

#### Función: `generate_slots_for_machine`
Generador automático de disponibilidad.
- **Parámetros:** `db`, `machine_id`, `start_date`, `days`, `start_hour`, `end_hour`.
- **Lógica:**
    1. Itera por el número de días solicitados.
    2. Para cada día, itera por las horas laborales definidas (`start_hour` a `end_hour`).
    3. Verifica si ya existe un slot en ese horario.
    4. Si no existe, crea un nuevo `AvailabilitySlot` con el precio base de la máquina.
    5. Hace commit de la transacción.

### Archivo: `app/services/bidding.py`

#### Función: `place_bid`
Motor central de subastas.
- **Parámetros:** `db`, `slot_id`, `user_id`, `amount`, `max_bid_amount` (opcional).
- **Reglas de Negocio:**
    1. **Validación:** Verifica disponibilidad del slot y que la oferta supere el mínimo requerido.
    2. **Normalización:** Si `max_bid_amount` es `None`, se establece igual a `amount` (Modo Manual).
    3. **Proxy Bidding vs Manual:**
        - Compara la nueva oferta con el `max_bid` del ganador actual.
        - Si `nuevo_max > actual_max`: El nuevo usuario gana. El precio se ajusta a `actual_max + incremento` (o al monto de la oferta manual si es mayor).
        - Si `nuevo_max <= actual_max`: El ganador actual se mantiene. El precio sube a `nuevo_max + incremento` para "defender" la posición del ganador actual.
    4. **Soft Close:** Si la oferta ocurre cerca del cierre (`SOFT_CLOSE_MINUTES`), extiende la subasta (`SOFT_CLOSE_EXTENSION`).
    5. **Notificaciones:** Si hay un cambio de ganador (Outbid), invoca a `notifications.send_notification` para alertar al perdedor.

### Archivo: `app/services/notifications.py`

#### Función: `send_notification`
Servicio central de mensajería.
- **Parámetros:** `db`, `user_id`, `type`, `title`, `message`, `payload`.
- **Lógica:**
    1. Crea un registro persistente en la tabla `Notification`.
    2. (Simulación) Imprime en consola el contenido del mensaje, representando el envío de un Email o Push Notification.

---

## 10. Testing y Despliegue

### Migraciones de Base de Datos (Alembic)
El proyecto utiliza Alembic para gestionar los cambios en el esquema de la base de datos.

**Comandos Principales:**
- **Generar nueva migración:**
  ```bash
  # Si se ejecuta desde el host local (fuera de Docker):
  POSTGRES_SERVER=localhost POSTGRES_PORT=5433 alembic revision --autogenerate -m "Descripción"
  ```
- **Aplicar migraciones (Actualizar DB):**
  ```bash
  POSTGRES_SERVER=localhost POSTGRES_PORT=5433 alembic upgrade head
  ```

### Inicialización de Datos (Seed)
Para facilitar el desarrollo y pruebas, se incluye un script que crea un **Superusuario** por defecto.

- **Archivo:** `app/initial_data.py`
- **Ejecución:**
  ```bash
  POSTGRES_SERVER=localhost POSTGRES_PORT=5433 python -m app.initial_data
  ```
- **Credenciales por defecto:**
  - Email: `admin@conmaq.com`
  - Password: `admin`

### Pruebas Automatizadas (Pytest)
Se ha configurado `pytest` para pruebas de integración.

- **Estructura:** Carpeta `app/tests/`.
- **Ejecución:**
  ```bash
  pytest
  ```
- **Escenarios Clave:**
  - `test_bidding_flow`: Verifica la lógica de Proxy Bidding.
  - `test_manual_bidding`: Verifica la lógica de ofertas manuales sin auto-incremento.
- **Nota:** Las pruebas requieren que la base de datos esté corriendo y accesible.

---
*Fin del Manual Técnico de Referencia*
