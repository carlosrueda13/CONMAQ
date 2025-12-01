# Manual Técnico de Referencia - Frontend CONMAQ

**Versión del Documento:** 1.0
**Fecha de Creación:** 30 de Noviembre de 2025
**Tecnología:** Flutter (Dart)
**Estado:** Fase 1 (Inicialización y Arquitectura)

---

## Tabla de Contenidos
1. [Introducción](#1-introducción)
2. [Arquitectura del Proyecto](#2-arquitectura-del-proyecto)
3. [Configuración y Diseño](#3-configuración-y-diseño)
4. [Módulo Core (Núcleo)](#4-módulo-core-núcleo)
5. [Gestión de Dependencias](#5-gestión-de-dependencias)
6. [Estructura de Directorios](#6-estructura-de-directorios)

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
*Fin del Manual Técnico*
