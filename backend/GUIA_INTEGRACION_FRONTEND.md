# Guía de Integración Frontend (Flutter/Dart) - Sistema CONMAQ

**Versión:** 1.0
**Fecha:** 25 de Noviembre de 2025
**Backend Stack:** Python (FastAPI) + PostgreSQL
**Frontend Stack Recomendado:** Flutter (Dart)

---

## 1. Introducción y Arquitectura

Esta guía está diseñada para el equipo de desarrollo móvil/web que implementará la interfaz de usuario del sistema CONMAQ. El backend expone una API RESTful documentada con OpenAPI (Swagger).

### Recomendaciones de Arquitectura (Flutter)
Para mantener la escalabilidad y robustez alineada con el backend, se recomienda:
- **Gestión de Estado:** Riverpod (v2.0+) o BLoC (v8.0+).
- **Cliente HTTP:** Dio (por su manejo de interceptores para JWT).
- **Modelos:** Freezed + JsonSerializable (para inmutabilidad y serialización segura).
- **Almacenamiento Seguro:** `flutter_secure_storage` para guardar el JWT.

---

## 2. Configuración del Entorno

### Base URLs
- **Desarrollo (Local):** `http://localhost:8000` (o `http://10.0.2.2:8000` para emulador Android).
- **Producción:** *[Pendiente de Deploy]*
- **Prefijo API:** `/api/v1`

### Swagger UI
Para ver los contratos en tiempo real y probar payloads:
- URL: `http://localhost:8000/docs`

---

## 3. Autenticación y Seguridad

El sistema utiliza **OAuth2 con Password Flow**.

### 3.1 Login
El endpoint de login **NO** espera un JSON body estándar, sino `application/x-www-form-urlencoded` (estándar OAuth2).

- **Endpoint:** `POST /api/v1/auth/login/access-token`
- **Body (Form Data):**
  - `username`: (String) El email del usuario.
  - `password`: (String) La contraseña.
- **Respuesta Exitosa (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUz...",
    "token_type": "bearer"
  }
  ```

**Implementación en Dart (Dio):**
```dart
Future<String> login(String email, String password) async {
  final response = await dio.post(
    '/auth/login/access-token',
    data: {'username': email, 'password': password},
    options: Options(contentType: Headers.formUrlEncodedContentType),
  );
  return response.data['access_token'];
}
```

### 3.2 Manejo del Token
1.  **Almacenamiento:** Guardar el `access_token` en almacenamiento seguro.
2.  **Interceptors:** En cada petición subsiguiente, inyectar el header:
    `Authorization: Bearer <access_token>`

### 3.3 Registro de Usuario
- **Endpoint:** `POST /api/v1/users/`
- **Body (JSON):**
  ```json
  {
    "email": "cliente@ejemplo.com",
    "password": "segura",
    "full_name": "Juan Perez",
    "phone": "+573001234567",
    "role": "client" // Opcional, default es client
  }
  ```

---

## 4. Módulo de Maquinaria (Catálogo)

### 4.1 Listado de Máquinas
- **Endpoint:** `GET /api/v1/machines/`
- **Filtros (Query Params):**
  - `status`: (Opcional) ej. `available`, `rented`.
  - `serial_number`: (Opcional) Búsqueda exacta.
- **Modelo Dart Sugerido:**
  ```dart
  class Machine {
    final int id;
    final String name;
    final String serialNumber;
    final double priceBasePerHour;
    final String status;
    final Map<String, dynamic>? specs; // Especificaciones técnicas flexibles
    final List<String>? photos;
    // ... otros campos
  }
  ```

### 4.2 Disponibilidad (Calendario)
Para mostrar el calendario de una máquina:
- **Endpoint:** `GET /api/v1/machines/{id}/availability`
- **Query Params:** `start_date`, `end_date` (Formato ISO `YYYY-MM-DD`).
- **Respuesta:** Lista de `AvailabilitySlot`.
  ```json
  [
    {
      "id": 101,
      "start_time": "2025-11-26T08:00:00",
      "end_time": "2025-11-26T09:00:00",
      "is_available": true,
      "current_price": 150.0
    }
  ]
  ```
- **Lógica UI:**
  - Si `is_available` es `true` y `current_price` es `null` o igual al base -> Mostrar precio base.
  - Si `current_price` > precio base -> Mostrar "Oferta actual: $X".

---

## 5. Motor de Subastas (Bidding)

Este es el núcleo de la interacción. El frontend debe manejar dos modos de oferta.

### 5.1 Crear una Oferta
- **Endpoint:** `POST /api/v1/offers/`
- **Body (JSON):**
  ```json
  {
    "slot_id": 101,
    "amount": 120.0,    // Requerido: Tu oferta visible
    "max_bid": 150.0    // Opcional: Tu límite secreto (Proxy Bidding)
  }
  ```

### 5.2 Lógica de UI para Ofertas
Debes ofrecer al usuario dos opciones visuales:

1.  **"Oferta Manual" (Simple):**
    - El usuario ingresa solo un monto (ej. $120).
    - **Acción:** Enviar `amount: 120`, `max_bid: null` (o no enviar el campo).
    - **Comportamiento:** El sistema asume `max_bid = 120`. No habrá auto-incremento.

2.  **"Oferta Automática" (Avanzada):**
    - El usuario ingresa su oferta inicial (ej. $120) y su límite máximo (ej. $200).
    - **Acción:** Enviar `amount: 120`, `max_bid: 200`.
    - **Comportamiento:** El sistema ofertará por el usuario hasta llegar a $200 si es necesario.

### 5.3 Historial de Ofertas
- **Endpoint:** `GET /api/v1/offers/my-offers`
- **Uso:** Pantalla "Mis Subastas". Muestra si estás ganando (`winning`) o perdiendo (`outbid`).

---

## 6. Gestión de Reservas y Operaciones

Una vez que una oferta es ganadora (o se crea una reserva directa), el ciclo de vida operativo comienza.

### 6.1 Ciclo de Vida de la Reserva
El estado (`status`) fluye de la siguiente manera:
1.  `pending_payment`: Reserva creada, esperando pago.
2.  `confirmed`: Pago recibido, lista para iniciar.
3.  `active`: El cliente ha hecho **Check-in** y está usando la máquina.
4.  `completed`: El cliente ha hecho **Check-out**.
5.  `cancelled`: Cancelada antes de iniciar (Call-off).

### 6.2 Crear Reserva desde Oferta
- **Endpoint:** `POST /api/v1/bookings/from-offer/{offer_id}`
- **Uso:** Cuando el usuario gana una subasta, debe confirmar la reserva.
- **Respuesta:** Objeto `Booking`.

### 6.3 Operaciones de Campo (Check-in / Check-out)
Estas operaciones son críticas y requieren evidencia (fotos y nivel de combustible).

#### Check-in (Inicio de uso)
- **Endpoint:** `POST /api/v1/bookings/{booking_id}/check-in`
- **Body (JSON):**
  ```json
  {
    "start_fuel_level": 0.75, // 0.0 a 1.0 (75%)
    "start_photos": [
      "https://s3.aws.../foto1.jpg",
      "https://s3.aws.../foto2.jpg"
    ],
    "comments": "Máquina recibida en buen estado."
  }
  ```
- **Validación:** Solo permitido si el estado es `confirmed` y la hora actual es cercana al `start_time`.

#### Check-out (Fin de uso)
- **Endpoint:** `POST /api/v1/bookings/{booking_id}/check-out`
- **Body (JSON):**
  ```json
  {
    "end_fuel_level": 0.50,
    "end_photos": [ ... ],
    "comments": "Entrega finalizada."
  }
  ```
- **Nota:** Esto marca la reserva como `completed` y libera la máquina.

### 6.4 Cancelación (Call-off)
- **Endpoint:** `POST /api/v1/bookings/{booking_id}/call-off`
- **Body:** `{"reason": "Lluvia intensa"}`
- **Uso:** Para cancelar una reserva confirmada antes de iniciar.

### 6.5 Listado de Reservas
- **Endpoint:** `GET /api/v1/bookings/`
- **Filtros:** `status` (ej. `active` para ver qué tengo en uso ahora mismo).

---

## 7. Notificaciones y Watchlist

### 6.1 Watchlist (Favoritos)
- **Endpoint:** `POST /api/v1/watchlist/toggle`
- **Body:** `{"machine_id": 1}`
- **UX:** Botón de "Corazón" en el detalle de la máquina. Al pulsarlo, llama a este endpoint. Retorna si fue `added` o `removed`.

### 6.2 Notificaciones
- **Endpoint:** `GET /api/v1/notifications/`
- **Uso:** Centro de notificaciones.
- **Tipos de Evento:**
  - `outbid`: "Te han superado en la subasta X".
  - `won`: "Ganaste la subasta".
- **Polling:** Por ahora, el frontend debe consultar este endpoint periódicamente (ej. cada 30s) o usar "Pull to Refresh". (WebSockets están en roadmap futuro).

---

## 8. Manejo de Errores

El backend retorna errores estandarizados `HTTPException`.

- **Formato de Error:**
  ```json
  {
    "detail": "Mensaje descriptivo del error"
  }
  ```
- **Códigos Comunes:**
  - `400 Bad Request`: Datos inválidos (ej. oferta menor al mínimo).
  - `401 Unauthorized`: Token expirado o inválido -> **Acción:** Redirigir a Login.
  - `403 Forbidden`: No tienes permisos (ej. intentar crear máquina sin ser admin).
  - `404 Not Found`: Recurso no existe.

---

## 9. Flujo de Usuario Típico (Ejemplo)

1.  **Home:** `GET /machines/` -> Muestra lista de equipos.
2.  **Detalle:** Usuario toca una máquina -> Muestra specs y fotos.
3.  **Calendario:** Usuario selecciona "Ver Disponibilidad" -> `GET /machines/{id}/availability`.
4.  **Selección:** Usuario toca un slot (ej. 8:00 AM - 9:00 AM).
5.  **Oferta:**
    - Modal emergente: "¿Cuánto quieres ofertar?".
    - Input: Monto ($).
    - Checkbox opcional: "Activar Auto-puja hasta..." (habilita input `max_bid`).
    - Botón "Confirmar".
6.  **Envío:** `POST /offers/`.
7.  **Feedback:**
    - Éxito: Toast "Oferta realizada".
    - Error (400): "Tu oferta es muy baja, el mínimo es $X".
8.  **Reserva (Ganador):** Usuario recibe notificación de victoria y confirma -> `POST /bookings/from-offer/{id}`.
9.  **Check-in:** Al llegar al sitio, usuario sube fotos y nivel de combustible -> `POST /bookings/{id}/check-in`.
10. **Check-out:** Al finalizar, usuario reporta estado final -> `POST /bookings/{id}/check-out`.

---

**Nota para el equipo Frontend:**
Cualquier duda sobre los tipos de datos exactos, consulten el archivo `app/schemas/` en el repositorio backend o usen el Swagger UI local. ¡Éxito en el desarrollo!
