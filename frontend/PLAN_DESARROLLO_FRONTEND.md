# Plan de Desarrollo Frontend - CONMAQ (4 Días)

**Rol:** Lead Frontend Developer (Flutter/Dart)
**Objetivo:** Construir una aplicación móvil/web completa, integrada con el backend FastAPI, siguiendo arquitectura limpia y diseño "Liquid Glass", con soporte multi-rol (Cliente, Operador, Admin).
**Fecha de Inicio:** Día 1
**Fecha de Entrega:** Día 4 (Final del día)

---

## DÍA 1: Cimientos, Arquitectura y Seguridad (Completado)

### Mañana: Configuración del Entorno y Arquitectura Base
*   [x] Inicialización del Proyecto y Estructura de Carpetas.
*   [x] Gestión de Dependencias (`pubspec.yaml`).
*   [x] Sistema de Diseño (Theming) y Paleta de Colores.
*   [x] Capa de Red (Dio Client con Interceptores).

### Tarde: Autenticación y Gestión de Sesión
*   [x] Capa de Datos Auth (Modelos, DataSource, Repository).
*   [x] Almacenamiento Seguro (Token JWT).
*   [x] Gestión de Estado (AuthNotifier).
*   [x] UI: Splash Screen y Login Screen (Diseño Glass).

---

## DÍA 2: Identidad, Roles y Catálogo Inteligente

### Mañana: Catálogo y Navegación Base (Completado)
*   [x] Configuración de Router (`GoRouter`).
*   [x] Capa de Datos Machines (Modelos, DataSource, Repository).
*   [x] Home Screen (Catálogo con Grid y Búsqueda).
*   [x] Widget `MachineCard` (Diseño Glass).

### Tarde: Gestión de Identidad y Diferenciación de Roles

**Objetivo:** Establecer la infraestructura para múltiples actores y permitir el ingreso de nuevos clientes.

1.  **Registro de Usuarios (Sign Up):**
    *   **Pantalla `RegisterScreen`:** Formulario con Email, Password, Nombre Completo.
    *   **Conexión:** Endpoint `POST /api/v1/users/`.
    *   **Lógica:** Login automático post-registro o redirección al Login.

2.  **Enrutamiento Basado en Roles (RBAC):**
    *   **Actualizar Modelo `User`:** Asegurar que el campo `role` (`client`, `operator`, `admin`) se parsee correctamente.
    *   **Lógica de Redirección (`AuthNotifier`):**
        *   Si `role == client` -> Redirigir a `/home` (Catálogo).
        *   Si `role == operator` -> Redirigir a `/operator/dashboard`.
        *   Si `role == admin` -> Redirigir a `/admin/dashboard`.
    *   **Router:** Definir las nuevas rutas `/operator/dashboard` y `/admin/dashboard` (inicialmente Scaffolds vacíos con título).

3.  **Refinamiento del Catálogo (Vista Cliente):**
    *   **Provider Logic:** Modificar `MachinesNotifier.loadMachines()`.
    *   **Condición:** Si el usuario es `client`, inyectar automáticamente el parámetro `status=available` en la petición al backend.
    *   **Resultado:** El cliente solo ve lo que puede rentar.

---

## DÍA 3: El Corazón del Negocio (Cliente) y Operaciones (Operador)

### Mañana: Detalle, Reservas y Portal del Operador

**Objetivo:** Permitir al cliente reservar y al operador gestionar su día a día.

1.  **Detalle de Máquina (Cliente/Admin):**
    *   Pantalla `MachineDetailScreen`.
    *   **Cliente:** Ve botón "Reservar" / "Ofertar".
    *   **Admin:** Ve botón "Editar" / "Historial".
    *   **Specs:** Renderizado dinámico de especificaciones técnicas.

2.  **Portal del Operador (Dashboard):**
    *   **Endpoint:** `GET /api/v1/bookings/?status=confirmed,active`.
    *   **UI:** Lista de tareas del día (Reservas confirmadas que requieren atención).
    *   **Tarjeta de Tarea:** Muestra Máquina, Cliente, Hora y Tipo de Acción (Entregar/Recibir).

3.  **Flujo de Check-in/Check-out (Operador):**
    *   **Pantalla `OperationScreen`:**
        *   **Paso 1:** Slider de Combustible (0-100%).
        *   **Paso 2:** Evidencia Fotográfica (Integración `image_picker`).
        *   **Paso 3:** Comentarios.
    *   **Conexión:** Endpoints `POST .../check-in` y `.../check-out`.

### Tarde: Motor de Subastas y Mis Reservas (Cliente)

**Objetivo:** Implementar la lógica compleja de precios y seguimiento para el cliente.

1.  **Motor de Ofertas (Bidding):**
    *   **Disponibilidad:** Calendario visual (`table_calendar`) consumiendo `GET .../availability`.
    *   **Modal de Oferta:**
        *   Input Monto Simple.
        *   Switch "Auto-puja" (Proxy Bidding).
    *   **Validación:** Feedback inmediato si la oferta es muy baja.

2.  **Mis Reservas y Ofertas:**
    *   **Pantalla Unificada:** Tabs "Mis Ofertas" (En curso) y "Mis Reservas" (Ganadas).
    *   **Estados Visuales:**
        *   Winning (Verde/Dorado).
        *   Outbid (Rojo + Botón "Contraofertar").
        *   Confirmed (Azul + Instrucciones).

---

## DÍA 4: Administración, Pagos y Cierre

### Mañana: Portal del Administrador y Pagos

**Objetivo:** Dar control total al admin y monetizar la plataforma.

1.  **Portal Admin (Dashboard):**
    *   **Métricas:** Tarjetas con Ingresos Totales y Ocupación (`GET /metrics/...`).
    *   **Gestión Global:** Lista maestra de todas las reservas con opción de cancelación forzada (`call-off`).

2.  **Integración de Pagos (Stripe):**
    *   **Flujo Cliente:**
        *   Botón "Pagar" en reservas con estado `pending_payment`.
        *   Integración `flutter_stripe` para procesar tarjeta.
        *   Confirmación al backend.

### Tarde: Pulido Final, Testing Multi-Rol y Entrega

**Objetivo:** Asegurar que los tres mundos convivan sin errores.

1.  **Testing de Flujos Cruzados:**
    *   **Escenario 1:** Cliente se registra -> Oferta -> Gana.
    *   **Escenario 2:** Admin ve la reserva -> Operador hace Check-in -> Cliente usa -> Operador hace Check-out.
    *   **Validación:** Verificar que cada usuario solo vea lo que le corresponde.

2.  **Pulido Visual (Liquid Glass):**
    *   Revisión de contrastes y legibilidad en todos los portales.
    *   Animaciones de transición entre estados.

3.  **Build y Entrega:**
    *   Generación de APK/Web Build.
    *   Documentación final actualizada con la arquitectura de roles.

---

**Entregable Final:** Una aplicación unificada que se comporta como tres herramientas distintas según quién la use, cubriendo todo el ciclo de vida del negocio de alquiler.