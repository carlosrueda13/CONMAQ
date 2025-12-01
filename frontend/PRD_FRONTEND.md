# PRD - Frontend: Plataforma de Agendamiento CONMAQ

**Versión:** 1.0
**Fecha:** 30 de Noviembre de 2025
**Autor:** Equipo de Desarrollo Frontend (GitHub Copilot)
**Estado:** Borrador Inicial

---

## 1. Visión del Producto

Desarrollar una experiencia de usuario (UX) de clase mundial para la plataforma de renta de maquinaria CONMAQ. La aplicación debe ser **multiplataforma** (iOS, Android, Web) utilizando **Flutter**, destacándose por un diseño **moderno, minimalista y sofisticado**, inspirado en las últimas tendencias de diseño de Apple (Liquid Glass / Glassmorphism).

El objetivo es que la complejidad del sistema de subastas y agendamiento sea invisible para el usuario, presentando una interfaz fluida, intuitiva y altamente reactiva.

---

## 2. Especificaciones Técnicas y Stack

- **Framework:** Flutter (Dart).
- **Plataformas:** iOS, Android, Web (Responsive).
- **Gestión de Estado:** Riverpod (Recomendado por robustez) o BLoC.
- **Cliente HTTP:** Dio (Manejo de interceptores, tokens y errores).
- **Almacenamiento Local:** `flutter_secure_storage` (Tokens), `shared_preferences` (Configuraciones simples).
- **Mapas:** Google Maps Flutter o Mapbox.
- **Pagos:** `flutter_stripe`.
- **Cámara/Galería:** `image_picker` (Para evidencias de Check-in/Check-out).

---

## 3. Sistema de Diseño (UI/UX)

### 3.1 Filosofía Visual: "Liquid Glass"
- **Estilo:** Minimalista, uso de transparencias, desenfoques (blur) y gradientes sutiles. Elementos que parecen flotar sobre el fondo.
- **Bordes:** Redondeados suaves (Apple style).
- **Sombras:** Suaves y difusas para dar profundidad sin saturar.
- **Animaciones:** Transiciones fluidas entre pantallas, micro-interacciones al ofertar o reservar.

### 3.2 Paleta de Colores
La identidad de marca se define por los siguientes colores, que deben usarse con elegancia:

| Color | RGB | Hex | Uso Sugerido |
| :--- | :--- | :--- | :--- |
| **Verde Oliva** | (87, 114, 25) | `#577219` | Acentos, estados de éxito, botones secundarios. |
| **Azul Profundo** | (9, 38, 72) | `#092648` | Color primario, fondos oscuros, textos principales, barras de navegación. |
| **Dorado Ámbar** | (212, 158, 30) | `#D49E1E` | Call to Action (CTA), alertas, iconos destacados, estado "Winning". |

*Nota: En el modo oscuro (si se implementa), el Azul Profundo dominará los fondos.*

### 3.3 Tipografía
- **Fuente Principal:** San Francisco (iOS), Roboto (Android) o una fuente geométrica moderna como **Poppins** o **Inter** para unificar la web.
- **Legibilidad:** Alta prioridad en textos de precios y estados de subasta.

### 3.4 Personalización (White-label friendly)
- La arquitectura debe permitir cambiar fácilmente el **Logo** (Splash Screen y Headers) y la **Paleta de Colores** desde un archivo de configuración central (`AppTheme`).

---

## 4. Módulos y Requerimientos Funcionales

### 4.1 Onboarding y Autenticación
- **Splash Screen:**
  - Diseño limpio con el logo centrado y animación de entrada.
  - Carga inicial de configuraciones.
- **Login:**
  - Formulario minimalista (Email/Password).
  - Integración con endpoint `OAuth2` (`application/x-www-form-urlencoded`).
  - Manejo de errores amigable (Credenciales inválidas).
- **Registro:**
  - Formulario paso a paso para no abrumar (Datos básicos -> Contacto).

### 4.2 Catálogo de Maquinaria (Home)
- **Vista de Lista/Grid:** Tarjetas de máquinas con foto principal, nombre, precio base y estado (Disponible/Rentada).
- **Filtros:**
  - Barra de búsqueda (por nombre/serial).
  - Filtros rápidos (Estado, Tipo).
  - *Feature Web:* Vista de mapa interactivo mostrando ubicaciones de equipos.
- **Detalle de Máquina:**
  - Carrusel de imágenes (Hero animation).
  - Especificaciones técnicas (Specs JSON renderizado bonito).
  - Botón flotante o fijo: "Ver Disponibilidad" o "Añadir a Watchlist" (Corazón).

### 4.3 Disponibilidad y Subastas (Core)
- **Calendario Interactivo:**
  - Vista mensual/semanal.
  - Indicadores visuales de slots: Verde (Libre), Rojo (Ocupado), Amarillo (Tu oferta).
- **Interfaz de Oferta (Bidding Sheet):**
  - Modal "Bottom Sheet" con efecto Glassmorphism.
  - **Modo Manual:** Input simple de precio.
  - **Modo Auto (Proxy):** Switch para activar "Oferta Máxima Automática".
  - Feedback inmediato: Toast/Snackbar de éxito o error (ej. "Oferta muy baja").
- **Mis Ofertas:**
  - Lista en tiempo real de subastas activas.
  - Estados claros: "Ganando" (Verde/Dorado), "Superado" (Rojo/Alerta).

### 4.4 Gestión de Reservas (Bookings)
- **Listado de Reservas:**
  - Pestañas: Activas, Pendientes de Pago, Historial.
- **Flujo de Pago:**
  - Integración con Stripe Sheet.
  - Pantalla de confirmación de éxito.
- **Operaciones de Campo (Check-in / Check-out):**
  - **Wizard de Pasos:**
    1. Confirmar hora.
    2. Nivel de combustible (Slider interactivo).
    3. Evidencia Fotográfica (Cámara integrada o Galería).
    4. Firma digital (opcional) o confirmación simple.
  - Subida de imágenes optimizada.

### 4.5 Perfil y Notificaciones
- **Centro de Notificaciones:**
  - Lista de alertas (Outbid, Won, System).
  - Marcar como leídas.
- **Watchlist:**
  - Acceso rápido a máquinas favoritas.
- **Ajustes:**
  - Cerrar sesión.
  - Cambiar tema (Claro/Oscuro - Opcional).

---

## 5. Arquitectura de Software (Frontend)

Se seguirá una arquitectura limpia (**Clean Architecture**) para garantizar mantenibilidad y testabilidad.

```
lib/
├── config/             # Temas, rutas, constantes
├── core/               # Utilidades, errores, interceptores Dio
├── data/               # Repositorios, fuentes de datos (API calls)
│   ├── models/         # Modelos serializables (Freezed)
│   └── repositories/   # Implementación de repositorios
├── domain/             # Entidades, interfaces de repositorios
├── presentation/       # UI (Widgets, Pages, Providers/BLoCs)
│   ├── common/         # Widgets reutilizables (Botones, Inputs)
│   ├── auth/           # Pantallas de login/registro
│   ├── home/           # Catálogo
│   ├── bidding/        # Lógica de subastas
│   └── bookings/       # Gestión de reservas
└── main.dart
```

---

## 6. Integración con Backend

Referencia directa a la documentación técnica del backend (`backend/GUIA_INTEGRACION_FRONTEND.md`).

- **Base URL:** Configurable por entorno (`.env`).
- **Seguridad:**
  - Almacenamiento seguro de JWT (`flutter_secure_storage`).
  - Interceptor de Dio para inyectar `Authorization: Bearer <token>` automáticamente.
  - Interceptor para manejar `401 Unauthorized` (Logout automático).

---

## 7. Plan de Desarrollo (Fases)

1.  **Fase 1: Fundamentos (Semana 1)**
    - Setup del proyecto Flutter.
    - Configuración de arquitectura, rutas y tema (Colores/Fuentes).
    - Implementación de Capa de Red (Dio Client).
    - Pantallas: Splash, Login.

2.  **Fase 2: Catálogo y Navegación (Semana 2)**
    - Home Page con listado de máquinas.
    - Detalle de máquina.
    - Integración de Watchlist.

3.  **Fase 3: Core de Negocio - Subastas (Semana 3)**
    - Calendario de disponibilidad.
    - Lógica de ofertas (Manual y Proxy).
    - Pantalla "Mis Ofertas".

4.  **Fase 4: Operaciones y Pagos (Semana 4)**
    - Flujo de Reservas.
    - Integración Stripe.
    - Check-in / Check-out con fotos.

5.  **Fase 5: Pulido y Web (Semana 5)**
    - Adaptación responsive para Web.
    - Animaciones y micro-interacciones "Liquid Glass".
    - Testing y corrección de bugs.

---

**Notas Finales:**
Este frontend debe ser un reflejo de la calidad y modernidad de la marca CONMAQ. La prioridad es la **estabilidad** en la integración con el backend y la **belleza** en la interfaz de usuario.
