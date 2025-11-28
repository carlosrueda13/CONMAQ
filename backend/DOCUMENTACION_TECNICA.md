# Manual Técnico de Referencia - Sistema CONMAQ

**Versión del Documento:** 1.3
**Fecha de Última Actualización:** 26 de Noviembre de 2025
**Estado:** Fase 3 (Operaciones y Reservas)

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
| `POSTGRES_PORT` | `str` | Puerto del servidor de base de datos. | "5433" |
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

#### Clase `Booking` (Hereda de `Base`)
Representa la reserva confirmada de una máquina.

**Columnas:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `user_id` | `Integer` | FK a `user.id`. |
| `machine_id` | `Integer` | FK a `machine.id`. |
| `start_time` | `DateTime` | Inicio de la reserva. |
| `end_time` | `DateTime` | Fin esperado de la reserva. |
| `actual_end_time` | `DateTime` | Fin real (Call-off). |
| `status` | `String` | `pending_payment`, `confirmed`, `active`, `completed`, `cancelled`. |
| `total_price` | `Float` | Precio final acordado. |
| `start_photos` | `JSON` | URLs de fotos al inicio (Check-in). |
| `end_photos` | `JSON` | URLs de fotos al final (Check-out). |
| `start_fuel_level` | `Float` | Nivel de combustible al inicio. |
| `end_fuel_level` | `Float` | Nivel de combustible al final. |

#### Clase `Transaction` (Hereda de `Base`)
Registra los movimientos financieros asociados a una reserva.

**Columnas:**
| Nombre | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | `Integer` | PK. |
| `booking_id` | `Integer` | FK a `booking.id`. |
| `amount` | `Float` | Monto de la transacción. |
| `currency` | `String` | Moneda (default "USD"). |
| `status` | `String` | `pending`, `completed`, `failed`. |
| `provider_transaction_id` | `String` | ID externo (ej. Stripe PaymentIntent). |
| `type` | `String` | `payment`, `refund`. |

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

### Archivo: `app/schemas/booking.py`
DTOs para gestión de reservas.
- `BookingCreate`: Input para crear reserva (Admin/Internal).
- `BookingCheckIn`: Input para operación de Check-in (`start_fuel_level`, `start_photos`).
- `BookingCheckOut`: Input para operación de Check-out (`end_fuel_level`, `end_photos`).
- `Booking`: Output completo con estado y evidencia.

### Archivo: `app/schemas/transaction.py`
DTOs para pagos.
- `TransactionCreate`: Input interno para crear registro de pago.
- `PaymentIntentResponse`: Respuesta al iniciar pago (`client_secret`, `transaction_id`).
- `TransactionUpdate`: Input para confirmar pago (Webhook/Client).
- `Transaction`: Output completo.

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
- **Output:** JSON con `status`, `offer_id`, `slot_id`, `current_price`, `winner_id`, `auction_end_time`.
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

### Archivo: `app/api/v1/endpoints/bookings.py`

#### Endpoint: `create_booking_from_offer`
- **Ruta:** `POST /api/v1/bookings/from-offer/{offer_id}`
- **Lógica:** Convierte una oferta ganadora en una reserva. Copia precios y fechas del slot/oferta. Inicializa el estado en `pending_payment`.

#### Endpoint: `check_in`
- **Ruta:** `POST /api/v1/bookings/{id}/check-in`
- **Input:** `BookingCheckIn` (Fotos, Combustible).
- **Lógica:** Cambia estado a `active`, registra evidencia inicial.

#### Endpoint: `check_out`
- **Ruta:** `POST /api/v1/bookings/{id}/check-out`
- **Input:** `BookingCheckOut` (Fotos, Combustible).
- **Lógica:** Cambia estado a `completed`, registra evidencia final.

#### Endpoint: `call_off`
- **Ruta:** `POST /api/v1/bookings/{id}/call-off`
- **Lógica:** Marca el fin de uso (`actual_end_time`). Detiene el cobro de tiempo (lógica base).

### Archivo: `app/api/v1/endpoints/payments.py`

#### Endpoint: `create_payment_intent`
- **Ruta:** `POST /api/v1/payments/create-intent/{booking_id}`
- **Lógica:**
    1. Verifica que la reserva esté en `pending_payment`.
    2. Crea un registro `Transaction` en estado `pending`.
    3. (Mock) Genera un `client_secret` simulado.
    4. Retorna los datos necesarios para que el frontend procese el pago.

#### Endpoint: `confirm_payment`
- **Ruta:** `POST /api/v1/payments/confirm/{transaction_id}`
- **Lógica:**
    1. Actualiza `Transaction.status` a `completed`.
    2. Actualiza `Booking.status` a `confirmed`.
    3. Habilita la reserva para Check-in.

### Archivo: `app/api/v1/endpoints/metrics.py`

#### Endpoint: `get_financial_metrics`
- **Ruta:** `GET /api/v1/metrics/financial`
- **Permisos:** Admin Only.
- **Lógica:** Calcula ingresos totales (pagos completados) y pendientes.

#### Endpoint: `get_machine_metrics`
- **Ruta:** `GET /api/v1/metrics/machines`
- **Permisos:** Admin Only.
- **Lógica:** Retorna el Top 5 de máquinas más rentadas.

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

#### Función: `get_current_active_superuser`
Validación de privilegios de sistema.
- **Dependencia:** Llama a `get_current_active_user`.
- **Lógica:** Verifica `user.is_superuser`. Si es falso, lanza 400.
- **Uso:** Endpoints críticos de infraestructura (ej. crear máquinas, borrar usuarios).

#### Función: `get_current_active_admin`
Validación de rol administrativo.
- **Dependencia:** Llama a `get_current_active_user`.
- **Lógica:** Verifica si `user.role == "admin"` O si es superusuario.
- **Uso:** Endpoints de negocio sensibles (ej. ver métricas financieras, gestionar reservas globales).
- **Retorno:** Instancia del modelo `User` si cumple los requisitos.

### Rate Limiting (Limitación de Velocidad)
Implementado con `slowapi` para proteger la API.
- **Archivo:** `app/core/limiter.py`.
- **Configuración:**
    - Login: 5/minuto.
    - Registro: 3/minuto.
    - Ofertas: 10/minuto.
- **Respuesta:** `429 Too Many Requests`.

### CORS y Trusted Host
Configurados en `app/main.py`.
- **CORS:** Permite orígenes `localhost`, `localhost:3000`.
- **Trusted Host:** Protege contra ataques de Host Header.

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
Motor central de subastas. Implementa la lógica de Proxy Bidding y Soft Close.

- **Parámetros:**
    - `db`: Sesión de base de datos.
    - `slot_id`: ID del slot de disponibilidad.
    - `user_id`: ID del usuario que oferta.
    - `amount`: Monto visible de la oferta.
    - `max_bid_amount` (opcional): Monto máximo secreto para auto-puja.

- **Retorno:** Tupla `(AvailabilitySlot, Offer)`. Retorna el slot actualizado y la oferta creada.

- **Reglas de Negocio Detalladas:**
    1. **Validación de Entrada:**
        - El slot debe existir y estar disponible (`is_available=True`).
        - La subasta no debe haber finalizado (`now < auction_end_time`).
        - `max_bid` no puede ser menor que `amount`.
        - `max_bid` debe ser mayor o igual al precio actual + incremento mínimo (`MIN_INCREMENT = 10.0`).

    2. **Lógica de Proxy Bidding (Auto-Puja):**
        - **Caso 1: Primera Oferta.**
            - El usuario se convierte en ganador inmediatamente.
            - El precio actual se establece en el precio base (o el monto ofertado si no hay base).
        - **Caso 2: Competencia (Ya existe un ganador).**
            - Se compara el `max_bid` del nuevo usuario contra el `max_bid` del ganador actual.
            - **Escenario A (Nuevo Ganador):** Si `nuevo_max > actual_max`:
                - El nuevo usuario gana.
                - El precio sube a `actual_max + incremento`.
                - Se notifica al usuario anterior (`outbid`).
            - **Escenario B (Defensa Exitosa):** Si `nuevo_max <= actual_max`:
                - El ganador actual mantiene su posición.
                - El precio sube automáticamente a `nuevo_max + incremento` para superar al retador, sin exceder su propio límite.
                - La nueva oferta queda marcada como `outbid` inmediatamente.

    3. **Soft Close (Extensión de Tiempo):**
        - Si una oferta válida entra en los últimos `SOFT_CLOSE_MINUTES` (5 min) antes del cierre.
        - Se extiende la `auction_end_time` por `SOFT_CLOSE_EXTENSION` (10 min).
        - Esto previene el "sniping" (ofertas de último segundo) y permite una competencia justa.

### Archivo: `app/services/notifications.py`

#### Función: `send_notification`
Servicio central de mensajería.
- **Parámetros:** `db`, `user_id`, `type`, `title`, `message`, `payload`.
- **Lógica:**
    1. Crea un registro persistente en la tabla `Notification`.
    2. (Simulación) Imprime en consola el contenido del mensaje, representando el envío de un Email o Push Notification.

### Archivo: `app/services/payment.py`

#### Clase: `PaymentService`
Abstracción para pasarelas de pago.
- **`create_payment_intent`**: Prepara la transacción y comunica con el proveedor (Stripe Mock).
- **`confirm_payment`**: Maneja la lógica post-pago (actualización de estados cruzados Booking/Transaction).

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
Se ha configurado `pytest` para pruebas de integración y unitarias.

- **Estructura:** Carpeta `app/tests/`.
- **Ejecución:**
  ```bash
  pytest
  ```
- **Escenarios Clave:**
  - `test_bookings.py`: Flujo completo de integración (Oferta -> Reserva -> Pago -> Check-in/out).
  - `test_bidding.py`: Pruebas unitarias del motor de subastas.
    - **Manual Bidding:** Verifica que una oferta simple supere a la anterior.
    - **Proxy Bidding (Defensa):** Verifica que un `max_bid` alto defienda automáticamente la posición del ganador ante ofertas menores.
    - **Proxy Bidding (Overtake):** Verifica que una nueva oferta con `max_bid` superior desplace al ganador actual y ajuste el precio correctamente.
    - **Soft Close:** Verifica matemáticamente que una oferta en los últimos minutos extienda la fecha de fin (`auction_end_time`).
- **Nota:** Las pruebas de integración requieren DB activa. Las unitarias usan Mocks.

### Generación de Datos (Seeding)
Script para poblar la base de datos con información realista usando `Faker`.
- **Archivo:** `app/db/seeds.py`.
- **Contenido:** 50 máquinas, 20 usuarios, historial de ofertas.
- **Ejecución:** Automática al iniciar `app/initial_data.py` si la DB está vacía.

---
*Fin del Manual Técnico de Referencia*
