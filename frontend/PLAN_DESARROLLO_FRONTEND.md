# Plan de Desarrollo Frontend - CONMAQ (4 Días)

**Rol:** Lead Frontend Developer (Flutter/Dart)
**Objetivo:** Construir una aplicación móvil/web completa, integrada con el backend FastAPI, siguiendo arquitectura limpia y diseño "Liquid Glass".
**Fecha de Inicio:** Día 1
**Fecha de Entrega:** Día 4 (Final del día)

---

## DÍA 1: Cimientos, Arquitectura y Seguridad

### Mañana: Configuración del Entorno y Arquitectura Base

**Objetivo:** Establecer una base sólida de código que soporte escalabilidad y mantenibilidad.

1.  **Inicialización del Proyecto:**
    *   Ejecutar: `flutter create --org com.conmaq --platforms ios,android,web frontend`
    *   Configurar `.gitignore` estándar para Flutter.

2.  **Gestión de Dependencias (`pubspec.yaml`):**
    *   **Core:** `flutter_riverpod` (Estado), `go_router` (Navegación), `dio` (HTTP), `get_it` (Inyección dependencias).
    *   **Data:** `freezed_annotation`, `json_annotation`, `flutter_secure_storage` (Tokens), `shared_preferences`.
    *   **UI:** `google_fonts`, `flutter_svg`, `cached_network_image`, `glassmorphism` (o implementación manual).
    *   **Dev:** `build_runner`, `freezed`, `json_serializable`.

3.  **Estructura de Carpetas (Clean Architecture):**
    *   Crear en `lib/`:
        *   `config/` (theme, router, constants).
        *   `core/` (errors, utils, api_client).
        *   `data/` (datasources, models, repositories_impl).
        *   `domain/` (entities, repositories_interfaces).
        *   `presentation/` (providers, screens, widgets).

4.  **Sistema de Diseño (Theming):**
    *   Crear `lib/config/theme/app_theme.dart`.
    *   Definir `ColorPalette`:
        *   `primary`: Color(0xFF092648) (Azul Profundo).
        *   `secondary`: Color(0xFF577219) (Verde Oliva).
        *   `accent`: Color(0xFFD49E1E) (Dorado Ámbar).
    *   Configurar `ThemeData` global con fuentes (Poppins/Inter) y estilos de Inputs (Bordes redondeados, transparencias).

5.  **Capa de Red (Networking):**
    *   Implementar `lib/core/api/dio_client.dart`.
    *   Configurar `BaseOptions` con `baseUrl` desde variables de entorno (`.env`).
    *   **Crucial:** Configurar Interceptores para logging (`PrettyDioLogger`) y manejo de errores genérico.

### Tarde: Autenticación y Gestión de Sesión

**Objetivo:** Permitir que los usuarios inicien sesión y mantener la seguridad del token.

1.  **Capa de Datos (Auth):**
    *   Crear modelos: `LoginRequest`, `TokenResponse`, `User`.
    *   Implementar `AuthDataSource` con método `login(username, password)` apuntando a `/api/v1/auth/login/access-token`.
    *   **Nota:** Recordar enviar como `x-www-form-urlencoded`.

2.  **Almacenamiento Seguro:**
    *   Implementar servicio `StorageService` usando `flutter_secure_storage`.
    *   Métodos: `saveToken`, `getToken`, `deleteToken`.

3.  **Gestión de Estado (Auth):**
    *   Crear `AuthProvider` (Riverpod `StateNotifier`).
    *   Estados: `AuthStatus.checking`, `AuthStatus.authenticated`, `AuthStatus.unauthenticated`.
    *   Lógica: Al iniciar la app, leer token del storage. Si existe, validar (o asumir válido temporalmente).

4.  **UI de Autenticación:**
    *   **Splash Screen:** Logo centrado, fondo gradiente, lógica de redirección basada en `AuthStatus`.
    *   **Login Screen:**
        *   Diseño "Glass": Contenedor con `BackdropFilter`, bordes blancos semitransparentes.
        *   Validación de formulario.
        *   Manejo de errores (Snackbar "Credenciales incorrectas").

---

## DÍA 2: Catálogo, Navegación y Experiencia de Usuario

### Mañana: Navegación y Listado de Maquinaria

**Objetivo:** Mostrar el inventario disponible de forma atractiva y eficiente.

1.  **Configuración de Router:**
    *   Configurar `GoRouter` en `lib/config/router/app_router.dart`.
    *   Rutas: `/splash`, `/login`, `/home`, `/machine/:id`.
    *   Redirección: Si no está autenticado y trata de ir a `/home`, mandar a `/login`.

2.  **Capa de Datos (Machines):**
    *   Modelo `Machine` (Freezed) mapeando la respuesta de `/api/v1/machines/`.
    *   `MachineRepository` con método `getMachines({status, serial})`.

3.  **Home Screen (Catálogo):**
    *   Implementar `SliverGrid` para rendimiento.
    *   **Widget `MachineCard`:**
        *   Imagen principal (usar `CachedNetworkImage`).
        *   Precio por hora destacado en color Dorado.
        *   Indicador de estado (Disponible/Rentado).
        *   Efecto Glassmorphism en el footer de la tarjeta.

4.  **Búsqueda y Filtros:**
    *   Implementar `SearchBar` en el `SliverAppBar`.
    *   Lógica de filtrado local o remota (según API).

### Tarde: Detalle de Producto y Watchlist

**Objetivo:** Convencer al usuario de rentar y permitirle guardar favoritos.

1.  **Machine Detail Screen:**
    *   Uso de `Hero` animation para la transición de la imagen desde el Home.
    *   Sección de "Especificaciones": Renderizar el JSON de `specs` en una grilla limpia.
    *   Mapa estático (o botón a mapa) mostrando ubicación (`lat`, `lng`).

2.  **Watchlist (Favoritos):**
    *   Endpoint: `POST /api/v1/watchlist/toggle`.
    *   UI: Botón de "Corazón" flotante o en la barra superior.
    *   Estado: Debe reflejar si el usuario ya sigue la máquina (requiere consultar `GET /watchlist` al cargar).

3.  **Bottom Navigation Bar:**
    *   Implementar `ShellRoute` en GoRouter para mantener la barra de navegación persistente.
    *   Tabs: Home, Mis Ofertas, Reservas, Perfil.

---

## DÍA 3: El Corazón del Negocio (Subastas y Disponibilidad)

### Mañana: Calendario y Motor de Ofertas

**Objetivo:** Permitir al usuario visualizar disponibilidad y realizar ofertas complejas.

1.  **Disponibilidad (Calendar):**
    *   Endpoint: `GET /api/v1/machines/{id}/availability`.
    *   UI: Widget de Calendario (ej. `table_calendar` personalizado).
    *   Lógica visual:
        *   Días con slots disponibles: Punto verde.
        *   Al seleccionar día: Mostrar lista de horas (Slots) abajo.
        *   Slot Card: Muestra hora inicio/fin y **Precio Actual**.

2.  **Lógica de Ofertas (Bidding):**
    *   **Bidding Sheet (Modal):**
        *   Diseño sofisticado con fondo desenfocado.
        *   Mostrar: "Oferta actual más alta" y "Tu oferta".
    *   **Formulario:**
        *   Input `Monto Oferta`.
        *   Switch `Oferta Automática` -> Despliega Input `Monto Máximo`.
    *   Endpoint: `POST /api/v1/offers/`.
    *   Validación: El monto no puede ser menor al actual + incremento.

### Tarde: Gestión de Ofertas y Tiempo Real

**Objetivo:** Mantener al usuario informado sobre el estado de sus pujas.

1.  **Pantalla "Mis Ofertas":**
    *   Endpoint: `GET /api/v1/offers/my-offers`.
    *   Diseño de tarjeta de oferta:
        *   Estado **WINNING**: Borde Dorado/Verde, texto "Vas ganando".
        *   Estado **OUTBID**: Borde Rojo, botón "Contraofertar" (Lleva al Bidding Sheet).

2.  **Notificaciones y Polling:**
    *   Como no hay WebSockets aún, implementar `Timer` periódico (cada 30s) en el `OffersProvider` para refrescar la lista.
    *   **Centro de Notificaciones:**
        *   Endpoint: `GET /api/v1/notifications/`.
        *   UI: Lista simple con iconos según tipo (`outbid`, `won`).

---

## DÍA 4: Operaciones, Pagos y Entrega Final

### Mañana: Gestión de Reservas y Operaciones de Campo

**Objetivo:** Cerrar el ciclo de renta y manejar la evidencia física.

1.  **Listado de Reservas:**
    *   Endpoint: `GET /api/v1/bookings/`.
    *   Filtros visuales: Activas (En curso), Pendientes (De pago), Historial.

2.  **Check-in / Check-out (Evidencia):**
    *   Integrar `image_picker`.
    *   **UI de Wizard:**
        *   Paso 1: Slider de Combustible (0% a 100%).
        *   Paso 2: Grid de fotos (Botón "Tomar Foto").
        *   Paso 3: Comentarios y Enviar.
    *   Endpoints:
        *   `POST .../check-in` (Al inicio).
        *   `POST .../check-out` (Al final).

### Tarde: Pagos, Pulido Visual y Testing

**Objetivo:** Monetización y calidad final.

1.  **Integración de Pagos (Stripe):**
    *   Configurar `flutter_stripe`.
    *   Flujo:
        1.  Botón "Pagar Ahora" en reserva pendiente.
        2.  Llamar backend: `POST /payments/create-intent`.
        3.  Recibir `client_secret`.
        4.  `Stripe.instance.initPaymentSheet(...)`.
        5.  `Stripe.instance.presentPaymentSheet()`.
        6.  Al éxito, llamar backend: `POST /payments/confirm`.

2.  **Pulido Visual (The "Apple" Touch):**
    *   Revisar todas las sombras y bordes.
    *   Asegurar que los efectos de "Glassmorphism" no afecten la legibilidad.
    *   Añadir transiciones de página (`CupertinoPageTransition` o `FadeThrough`).
    *   Icono de la App y Splash nativo (`flutter_native_splash`).

3.  **Testing Manual y Build:**
    *   Recorrido completo: Login -> Buscar -> Ofertar -> Ganar -> Pagar -> Check-in -> Check-out.
    *   Generar APK/IPA (o web build) para entrega.

---

**Entregable Final:** Código fuente completo en repositorio, APK de prueba y documentación de despliegue.
