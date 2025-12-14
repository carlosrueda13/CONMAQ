# Manual Técnico de Referencia - Frontend CONMAQ

**Versión del Documento:** 1.1 (Revisión Post-Corrección Día 1)
**Fecha de Actualización:** 30 de Noviembre de 2025
**Tecnología:** Flutter (Dart)
**Estado:** Fase 1 (Inicialización, Arquitectura y Autenticación)

---

## Tabla de Contenidos
1. [Introducción](#1-introducción)
2. [Arquitectura del Proyecto](#2-arquitectura-del-proyecto)
3. [Configuración y Diseño](#3-configuración-y-diseño)
4. [Módulo Core (Núcleo)](#4-módulo-core-núcleo)
5. [Gestión de Dependencias](#5-gestión-de-dependencias)
6. [Estructura de Directorios](#6-estructura-de-directorios)
7. [Módulo de Autenticación (Detalle de Implementación)](#7-módulo-de-autenticación-detalle-de-implementación)
8. [Consideraciones de Desarrollo y Linter](#8-consideraciones-de-desarrollo-y-linter)

---

## 1. Introducción

Este documento constituye la referencia técnica definitiva para el desarrollo del frontend de la plataforma CONMAQ. Su propósito es guiar a los desarrolladores en la comprensión de la arquitectura, los patrones de diseño y las decisiones técnicas tomadas para construir una aplicación móvil y web robusta, escalable y mantenible.

El frontend está construido sobre **Flutter**, permitiendo un despliegue multiplataforma (iOS, Android, Web) desde una única base de código, integrándose mediante API REST con el backend desarrollado en Python/FastAPI.

---

## 2. Arquitectura del Proyecto

El proyecto sigue estrictamente los principios de **Clean Architecture** (Arquitectura Limpia), dividiendo el código en capas concéntricas de responsabilidad. Esto asegura que la lógica de negocio sea independiente de la interfaz de usuario, bases de datos o servicios externos.

### 2.1. Capas de la Aplicación

#### A. Capa de Presentación (`lib/presentation`)
Es la capa más externa, responsable de pintar la UI y manejar la interacción con el usuario.
- **Widgets:** Componentes visuales reutilizables.
- **Screens:** Pantallas completas que componen el flujo de navegación.
- **Providers (State Management):** Usamos **Riverpod** para gestionar el estado. Los providers actúan como intermediarios, escuchando cambios en la capa de dominio y actualizando la UI reactivamente.

#### B. Capa de Dominio (`lib/domain`)
Es el núcleo de la aplicación. **No debe tener dependencias de Flutter** (widgets) ni de librerías externas de datos (como Dio o Firebase).
- **Entities:** Objetos de negocio puros (POJOs) que representan los conceptos del sistema (ej. `User`, `Machine`).
- **Repositories Interfaces:** Contratos abstractos que definen qué operaciones se pueden realizar con los datos, pero no cómo se implementan.

#### C. Capa de Datos (`lib/data`)
Responsable de la implementación técnica de los contratos del dominio.
- **Models:** Extensiones de las Entidades que incluyen lógica de serialización/deserialización (JSON). Usamos `freezed` y `json_serializable`.
- **Data Sources:** Conexiones directas a fuentes de datos (API REST, Base de Datos Local).
- **Repositories Implementations:** Implementan las interfaces del dominio, coordinando los Data Sources.

#### D. Capa Core/Config (`lib/core`, `lib/config`)
Utilidades transversales y configuración global.
- **Config:** Temas, Rutas, Inyección de Dependencias.
- **Core:** Manejo de errores, clientes HTTP, constantes.

---

## 3. Configuración y Diseño

### 3.1. Sistema de Diseño (`AppTheme`)
Ubicación: `lib/config/theme/app_theme.dart`

La aplicación implementa un diseño moderno basado en la filosofía "Liquid Glass" (Glassmorphism) y los lineamientos de Apple.

**Paleta de Colores:**
| Nombre | Hex | Uso |
| :--- | :--- | :--- |
| `primaryColor` | `#092648` | Fondos principales, textos de cabecera, botones primarios. |
| `secondaryColor` | `#577219` | Elementos de éxito, acentos naturales. |
| `accentColor` | `#D49E1E` | Call to Action (CTA), estados de alerta/atención. |
| `scaffoldBackgroundColor` | `#F5F5F7` | Fondo general (Gris claro estilo iOS). |

**Tipografía:**
Se utiliza **Poppins** (vía `google_fonts`) por su legibilidad y modernidad geométrica.

**Componentes Estilizados:**
- **Inputs:** `InputDecorationTheme` configurado con `filled: true`, color blanco semitransparente (`opacity 0.8`) y bordes redondeados (`borderRadius: 12`), simulando cristal.
- **Botones:** `ElevatedButtonTheme` con `primaryColor` y bordes redondeados.

### 3.2. Constantes (`ApiConstants`)
Ubicación: `lib/core/constants/api_constants.dart`

Centraliza todas las rutas de la API para evitar "magic strings" dispersos por el código.
- `baseUrl`: `http://localhost:8000/api/v1` (Configurable).
- Endpoints definidos estáticamente (ej. `loginEndpoint`, `machinesEndpoint`).

---

## 4. Módulo Core (Núcleo)

### 4.1. Cliente HTTP (`DioClient`)
Ubicación: `lib/core/api/dio_client.dart`

Se utiliza el paquete **Dio** en lugar del `http` estándar por sus capacidades avanzadas (interceptores, cancelación de peticiones, manejo global de configuración).

**Características:**
- **Singleton/Instancia Única:** Configurado para ser inyectado o instanciado una vez.
- **Timeouts:** 15 segundos para conexión y recepción.
- **Interceptors:**
    - **Logging:** En modo `kDebugMode`, imprime en consola cada Request (Método, Path, Headers, Body) y cada Response/Error. Esto facilita enormemente la depuración sin exponer datos sensibles en producción.
    - **Manejo de Errores:** (En desarrollo) Interceptará códigos 401 para cerrar sesión automáticamente.

---

## 5. Gestión de Dependencias

El archivo `pubspec.yaml` gestiona las librerías externas. A continuación, la justificación de las principales elecciones:

### Core & Arquitectura
- **`flutter_riverpod`:** Sistema de gestión de estado y de inyección de dependencias reactivo. Más robusto y seguro (compile-safe) que `Provider`.
- **`get_it`:** Service Locator para inyección de dependencias no relacionadas con la UI (ej. Repositorios).
- **`go_router`:** Gestión de navegación declarativa basada en URLs, esencial para soporte Web y Deep Linking.

### Datos & Red
- **`dio`:** Cliente HTTP potente.
- **`freezed_annotation` / `freezed`:** Generación de código para clases inmutables y Union Types (Sealed Classes). Reduce el boilerplate y errores en tiempo de ejecución.
- **`json_annotation` / `json_serializable`:** Serialización automática de JSON.
- **`flutter_secure_storage`:** Almacenamiento encriptado (Keychain en iOS, Keystore en Android) para guardar el JWT.

### UI & UX
- **`google_fonts`:** Carga dinámica de fuentes.
- **`flutter_svg`:** Renderizado de gráficos vectoriales de alta calidad.
- **`glassmorphism`:** Utilidades para efectos de desenfoque y transparencia.
- **`cached_network_image`:** Caché de imágenes para optimizar rendimiento y consumo de datos.

---

## 6. Estructura de Directorios

```
frontend/
├── lib/
│   ├── config/                 # Configuración global
│   │   ├── router/             # Definición de rutas (GoRouter)
│   │   └── theme/              # Tema de la app (Colores, Fuentes)
│   ├── core/                   # Núcleo compartido
│   │   ├── api/                # Cliente HTTP (Dio)
│   │   ├── constants/          # Constantes estáticas
│   │   ├── errors/             # Definición de Excepciones (Failures)
│   │   └── utils/              # Funciones de ayuda
│   ├── data/                   # Capa de Datos
│   │   ├── datasources/        # Fuentes de datos (Remote/Local)
│   │   ├── models/             # DTOs (Data Transfer Objects)
│   │   └── repositories_impl/  # Implementación de repositorios
│   ├── domain/                 # Capa de Dominio (Reglas de Negocio)
│   │   ├── entities/           # Objetos de negocio puros
│   │   └── repositories_interfaces/ # Contratos (Interfaces)
│   ├── presentation/           # Capa de Presentación (UI)
│   │   ├── providers/          # State Management (Riverpod)
│   │   ├── screens/            # Pantallas
│   │   └── widgets/            # Componentes reutilizables
│   └── main.dart               # Punto de entrada
├── pubspec.yaml                # Dependencias
└── analysis_options.yaml       # Reglas de Linter
```

---

## 7. Módulo de Autenticación (Detalle de Implementación)

Este módulo gestiona la identidad del usuario y la seguridad de la sesión. Fue implementado siguiendo estrictamente Clean Architecture.

### 7.1. Flujo de Datos
1.  **UI (`LoginScreen`):** Captura email y password. Invoca `ref.read(authProvider.notifier).login()`.
2.  **Provider (`AuthNotifier`):** Cambia estado a `checking`. Llama a `AuthRepository.login()`.
3.  **Repository (`AuthRepositoryImpl`):**
    - Llama a `AuthDataSource.login()` para obtener el token.
    - Guarda el token usando `StorageService`.
    - Llama a `AuthDataSource.getUserMe()` para obtener datos del usuario.
    - Retorna una entidad `User` o lanza una excepción.
4.  **DataSource (`AuthDataSource`):** Realiza peticiones HTTP (`POST /login/access-token`, `GET /users/me`) usando `Dio`.

### 7.2. Seguridad (Token JWT e Interceptores)
La seguridad se maneja en dos frentes: persistencia segura e inyección automática de credenciales.

#### A. Persistencia (`StorageService`)
- **Herramienta:** `flutter_secure_storage`.
- **Mecanismo:**
    - **iOS:** Keychain.
    - **Android:** Keystore (AES encryption).
- **Ciclo de Vida:** El token se guarda tras un login exitoso y se elimina al cerrar sesión.

#### B. Inyección de Token (`DioClient`)
Para garantizar que todas las peticiones autenticadas funcionen, se implementó un **Interceptor de Autenticación** en el cliente HTTP centralizado.
- **Ubicación:** `lib/core/api/dio_client.dart`.
- **Funcionamiento:**
    1.  Antes de enviar cualquier petición (`onRequest`), el interceptor consulta asíncronamente el `StorageService`.
    2.  Si existe un token válido, lo inyecta en el encabezado HTTP:
        `Authorization: Bearer <token>`
    3.  Si no hay token, la petición se envía sin credenciales (útil para el endpoint de login).
- **Inyección de Dependencias:** `DioClient` ahora depende de `StorageService`, lo cual se refleja en el grafo de proveedores de Riverpod (`auth_provider.dart`).

### 7.3. Gestión de Estado (`AuthNotifier`)
El estado de autenticación se modela como una clase `AuthState` con las siguientes propiedades:
- `authStatus`: Enum (`checking`, `authenticated`, `unauthenticated`).
- `user`: Objeto `User` (nullable).
- `errorMessage`: String para feedback de errores (nullable).

**Lógica de Redirección:**
El `AppRouter` (GoRouter) escucha los cambios en este provider.
- Si `authStatus == checking` -> Muestra `SplashScreen`.
- Si `authStatus == unauthenticated` -> Redirige a `/login`.
- Si `authStatus == authenticated` -> Redirige a `/home`.

### 7.4. Componentes de UI (Liquid Glass Login)
La pantalla de Login (`lib/presentation/screens/login_screen.dart`) implementa un diseño avanzado:
- **Fondo:** Gradiente lineal (`primaryColor` a `primaryColor` oscuro).
- **Efecto Glass:** Contenedor central con `BackdropFilter` (blur 10x) y color blanco con opacidad 0.1.
- **Feedback:**
    - `CircularProgressIndicator` dentro del botón de login durante la carga.
    - `ScaffoldMessenger` para mostrar errores de autenticación (ej. "Credenciales incorrectas").

---

## 8. Consideraciones de Desarrollo y Linter

Esta sección documenta las excepciones y reglas específicas aplicadas para garantizar la calidad del código y la compatibilidad entre librerías.

### 8.1. Compatibilidad Freezed vs Linter
**Problema:** La librería `freezed` utiliza anotaciones `@JsonKey` en los constructores de fábrica (`factory constructors`), mientras que el linter de Dart estándar espera que estas anotaciones estén en los campos de la clase. Esto genera advertencias de tipo `invalid_annotation_target`.

**Solución:** Se ha configurado la supresión explícita de esta regla en los archivos generados por Freezed.
- **Archivos Afectados:** `lib/data/models/auth/token_response.dart`, `lib/data/models/auth/user.dart`.
- **Implementación:** Se añade `// ignore_for_file: invalid_annotation_target` al inicio de cada archivo de modelo.

### 8.2. Interpolación de Cadenas
**Regla:** Se debe preferir siempre la interpolación de cadenas (`'${variable}texto'`) sobre la concatenación con el operador `+`.
- **Motivo:** Mejora la legibilidad y el rendimiento en Dart.
- **Ejemplo Correcto:** `_dioClient.dio.get('${ApiConstants.usersEndpoint}me')`.

### 8.3. Punto de Entrada (`main.dart`)
El archivo `main.dart` ha sido limpiado de todo código boilerplate (contador por defecto). Su única responsabilidad es:
1.  Inicializar el `ProviderScope` de Riverpod.
2.  Lanzar `MyApp`.
3.  Configurar `MaterialApp.router` con el tema y las rutas definidas.

---
*Fin del Manual Técnico*
