# Manual Técnico de Referencia - Sistema CONMAQ

**Versión del Documento:** 1.5
**Fecha de Última Actualización:** 30 de Noviembre de 2025
**Estado:** Fase 4 (Calidad y Estabilización)

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

El proyecto sigue una arquitectura en capas basada en **FastAPI**, diseñada para separar responsabilidades y facilitar el mantenimiento. Se ha implementado un patrón de **Capa de Servicios de Dominio** para desacoplar la lógica de negocio de la capa de transporte HTTP.

### Estructura de Directorios
- **`app/core`**: Contiene la configuración global y lógica de seguridad transversal.
- **`app/db`**: Maneja la conexión a la base de datos y la definición del ORM.
- **`app/models`**: Define las tablas de la base de datos (Entidades).
- **`app/schemas`**: Define los modelos Pydantic para validación de datos (Data Transfer Objects).
- **`app/services`**: **NUEVO**. Contiene la lógica de negocio pura, organizada por dominios.
- **`app/api`**: Contiene los endpoints (controladores) y dependencias. Ahora actúan como una capa delgada de entrada/salida.

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

## 7. Capa de Servicios (Lógica de Negocio)

Esta capa (`app/services/`) contiene toda la inteligencia del negocio. Los controladores API solo llaman a estas funciones.

### Archivo: `app/services/offer.py` (Antes `bidding.py`)
Motor central de subastas. Implementa la lógica de Proxy Bidding y Soft Close.
- **`place_bid`**: Gestiona la creación de ofertas, validación de reglas, actualización de precios y notificaciones.
- **`get_user_offers`**: Recupera historial de ofertas de un usuario.
- **`get_slot_offers`**: Recupera ofertas de un slot.

### Archivo: `app/services/booking.py`
Gestión del ciclo de vida de una reserva.
- **`create_booking_from_offer`**: Convierte una oferta ganadora en reserva.
- **`perform_check_in`**: Valida y registra el inicio de renta.
- **`perform_check_out`**: Valida y registra el fin de renta.
- **`perform_call_off`**: Gestiona devoluciones anticipadas.

### Archivo: `app/services/machine.py`
CRUD de máquinas y lógica de disponibilidad.
- **`generate_availability`**: Genera slots vacíos para el calendario.
- **`get_machines`**: Búsqueda con filtros.

### Archivo: `app/services/payment.py`
Abstracción para pasarelas de pago.
- **`create_payment_intent`**: Prepara la transacción.
- **`confirm_payment`**: Finaliza el pago y confirma la reserva.

### Archivo: `app/services/notifications.py`
Sistema de mensajería interna.
- **`send_notification`**: Crea y "envía" alertas.

### Archivo: `app/services/watchlist.py`
Gestión de favoritos.
- **`toggle_watchlist_item`**: Añade o quita máquinas de la lista de seguimiento.

### Archivo: `app/services/metrics.py`
Cálculo de indicadores clave.
- **`calculate_financial_metrics`**: Ingresos totales y pendientes.
- **`get_top_machines`**: Ranking de máquinas más populares.

---

## 8. Capa de API (Controladores)

Los controladores en `app/api/v1/endpoints/` ahora son "delgados". Su única responsabilidad es:
1. Recibir la petición HTTP.
2. Validar el esquema de entrada (Pydantic).
3. Obtener la sesión de DB.
4. Llamar al Servicio correspondiente.
5. Retornar la respuesta.

### Archivo: `app/api/v1/endpoints/auth.py`
*(Sin cambios mayores, maneja lógica de tokens)*

### Archivo: `app/api/v1/endpoints/users.py`
Delega a `user_service`.

### Archivo: `app/api/v1/endpoints/machines.py`
Delega a `machine_service`.

### Archivo: `app/api/v1/endpoints/offers.py`
Delega a `offer_service`.

### Archivo: `app/api/v1/endpoints/watchlist.py`
Delega a `watchlist_service`.

### Archivo: `app/api/v1/endpoints/notifications.py`
Delega a `notification_service`.

### Archivo: `app/api/v1/endpoints/bookings.py`
Delega a `booking_service`.

### Archivo: `app/api/v1/endpoints/payments.py`
Delega a `PaymentService`.

### Archivo: `app/api/v1/endpoints/metrics.py`
Delega a `metrics_service`.

---

## 9. Seguridad e Inyección de Dependencias

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

### Gestión de Dependencias
El proyecto utiliza un sistema de dependencias de dos niveles para garantizar reproducibilidad.

- **`requirements.in`**: Dependencias principales de producción.
- **`requirements-dev.in`**: Herramientas de desarrollo y testing.
- **`requirements.txt`**: Archivo generado (lock file) con versiones exactas para producción.
- **`requirements-dev.txt`**: Archivo generado para entorno de desarrollo.

**Instalación:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Pruebas Automatizadas (Pytest)
El proyecto cuenta con una suite de pruebas robusta ubicada en `backend/tests/`.

- **Estructura:**
    - `tests/api/v1/`: Pruebas de integración de endpoints.
    - `tests/services/`: Pruebas unitarias de lógica de negocio.
    - `tests/models/`: Pruebas de integridad de datos.
- **Configuración:** `tests/conftest.py` configura una base de datos SQLite en memoria para pruebas aisladas y rápidas.

**Ejecución:**
```bash
# Ejecutar todos los tests
pytest

# Ejecutar con reporte de cobertura
pytest --cov=app --cov-report=term-missing
```

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

### Generación de Datos (Seeding)
Script para poblar la base de datos con información realista usando `Faker`.
- **Archivo:** `app/db/seeds.py`.
- **Contenido:** 50 máquinas, 20 usuarios, historial de ofertas.
- **Ejecución:** Automática al iniciar `app/initial_data.py` si la DB está vacía.

## 11. Calidad de Código y CI/CD

### Análisis Estático
Se utilizan herramientas estándar de la industria configuradas en `pyproject.toml`.

- **Black**: Formateador de código.
- **Isort**: Ordenamiento de imports.
- **Ruff**: Linter rápido para detectar errores y problemas de estilo.
- **Mypy**: Verificación estática de tipos.

**Comandos de Verificación:**
```bash
# Formatear
black app
isort app

# Linting
ruff check app

# Type Checking
mypy app
```

### Integración Continua (GitHub Actions)
El flujo de trabajo `.github/workflows/backend-ci.yml` se ejecuta en cada `push` y `pull_request` a la rama `main`.

**Pasos del Pipeline:**
1.  **Setup**: Instala Python 3.11 y dependencias.
2.  **Lint**: Ejecuta Ruff.
3.  **Format Check**: Verifica que el código cumpla con Black e Isort.
4.  **Type Check**: Ejecuta Mypy.
5.  **Test**: Ejecuta la suite de Pytest con reporte de cobertura.

Si algún paso falla, el commit es rechazado.

---
*Fin del Manual Técnico de Referencia*
