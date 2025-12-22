# Informe de Avance: Día 2 - Tarde (Parcial)
**Fecha:** 14 de Diciembre de 2025
**Estado:** En Progreso
**Foco:** Gestión de Identidad, Roles y Control de Acceso (RBAC)

---

## 1. Introducción
Este documento detalla con precisión milimétrica los avances realizados durante la primera mitad de la sesión de la tarde del Día 2. El objetivo principal ha sido transformar la aplicación de una herramienta de visualización pasiva a una plataforma multi-actor capaz de distinguir entre **Clientes**, **Operadores** y **Administradores**.

---

## 2. Implementación de Registro de Usuarios (Sign Up)

### 2.1. Descripción General
Se ha construido el módulo de registro desde cero, permitiendo la creación de nuevas cuentas en el sistema. Este módulo no solo captura datos, sino que asigna roles específicos que determinarán la experiencia completa del usuario dentro de la app.

### 2.2. Componentes Desarrollados (Paso a Paso)

#### A. Capa de Datos (La Tubería)
1.  **Modificación de `AuthDataSource` (`auth_datasource.dart`):**
    *   **Acción:** Se añadió el método `register`.
    *   **Detalle:** Este método construye una petición HTTP `POST` al endpoint `/users/`.
    *   **Payload (Carga útil):** Envía un JSON con `{email, password, full_name, phone, role}`.
    *   **Respuesta:** Espera y procesa un objeto `User` devuelto por el backend.

2.  **Actualización del Repositorio (`auth_repository.dart` y `impl`):**
    *   **Interfaz:** Se definió la firma del método `register` en el contrato abstracto.
    *   **Implementación:** Se conectó la llamada del repositorio al datasource, manteniendo la arquitectura limpia.

#### B. Gestión de Estado (El Cerebro)
1.  **Lógica en `AuthNotifier` (`auth_provider.dart`):**
    *   **Nueva Función `register`:**
        *   **Paso 1:** Cambia el estado a `AuthStatus.checking` (muestra spinner de carga).
        *   **Paso 2:** Invoca `_authRepository.register(...)`.
        *   **Paso 3 (Crítico):** Al tener éxito, invoca inmediatamente a `login(...)` con las mismas credenciales.
        *   **Resultado:** El usuario queda registrado y autenticado en un solo flujo continuo, sin tener que ir al login manualmente.

#### C. Interfaz de Usuario (La Pantalla)
1.  **Creación de `RegisterScreen` (`register_screen.dart`):**
    *   **Ubicación:** `/lib/presentation/screens/register_screen.dart`.
    *   **Diseño:** Estilo "Glassmorphism" consistente con el Login.
    *   **Campos del Formulario:**
        *   **Nombre Completo:** Validación de no vacío.
        *   **Correo Electrónico:** Validación de formato email.
        *   **Teléfono:** Teclado numérico.
        *   **Rol (Selector):** Dropdown crítico para pruebas. Opciones:
            *   `Cliente` (Valor: `client`)
            *   `Operador` (Valor: `operator`)
            *   `Administrador` (Valor: `admin`)
        *   **Contraseña:** Mínimo 6 caracteres, con botón de "ver/ocultar".
    *   **Feedback Visual:** SnackBar rojo en caso de error (ej. email ya existe).

---

## 3. Sistema de Control de Acceso Basado en Roles (RBAC)

### 3.1. Descripción General
Se implementó la lógica de "tráfico" que dirige a cada usuario a su portal correspondiente. Ya no existe un único destino `/home`.

### 3.2. Arquitectura de Navegación

#### A. Definición de Rutas (`app_router.dart`)
Se expandió el mapa de carreteras de la aplicación con nuevas destinos:
1.  `/register`: La pantalla de registro creada.
2.  `/operator-dashboard`: El centro de comando para el personal de mantenimiento.
3.  `/admin-dashboard`: El panel de control para la gestión global.

#### B. Lógica de Redirección Inteligente
Se modificaron los "Guardas" de navegación en `LoginScreen` y `RegisterScreen`.

**Algoritmo de Decisión:**
1.  El usuario se autentica exitosamente.
2.  El sistema inspecciona el objeto `User` recibido.
3.  Se evalúa la propiedad `role`:
    *   **CASO 1: `role == 'client'`**
        *   **Acción:** Navegar a `/home`.
        *   **Experiencia:** Ve el catálogo de maquinaria para rentar.
    *   **CASO 2: `role == 'operator'`**
        *   **Acción:** Navegar a `/operator-dashboard`.
        *   **Experiencia:** Ve tareas de mantenimiento y entregas (Próximamente).
    *   **CASO 3: `role == 'admin'`**
        *   **Acción:** Navegar a `/admin-dashboard`.
        *   **Experiencia:** Ve métricas y gestión de usuarios (Próximamente).

#### C. Portales Específicos
1.  **Operator Dashboard (`operator_dashboard_screen.dart`):**
    *   Pantalla inicial con icono de ingeniería (Naranja).
    *   Botón de Logout funcional (redirige a `/login`).
2.  **Admin Dashboard (`admin_dashboard_screen.dart`):**
    *   Pantalla inicial con icono de administración (Rojo).
    *   Botón de Logout funcional.

---

## 4. Guía de Verificación (Cómo probar lo construido)

Para validar este desarrollo, siga estos pasos exactos:

1.  **Inicio:** Abra la aplicación. Debería ver el Splash y luego el Login.
2.  **Navegación al Registro:** Pulse el texto "¿No tienes cuenta? Regístrate".
3.  **Prueba de Operador:**
    *   Llene el formulario.
    *   En "Rol", seleccione **"Operador"**.
    *   Pulse "REGISTRARSE".
    *   **Resultado Esperado:** Debe ser redirigido automáticamente a una pantalla con título "Panel de Operador" e icono naranja.
4.  **Ciclo de Logout:**
    *   Pulse el icono de "Salida" en la barra superior.
    *   **Resultado Esperado:** Regreso a la pantalla de Login.
5.  **Prueba de Admin:**
    *   Repita el registro con un nuevo email.
    *   Seleccione Rol **"Administrador"**.
    *   **Resultado Esperado:** Redirección al "Panel de Administrador" (Icono Rojo).

---

## 5. Próximos Pasos (Resto de la Tarde)
El sistema de identidad está vivo. El siguiente paso es refinar la vista del **Cliente** en el catálogo para asegurar que solo vea maquinaria disponible, completando así la visión de seguridad y experiencia de usuario personalizada.
