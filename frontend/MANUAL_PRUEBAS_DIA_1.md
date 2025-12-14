# Manual de Pruebas - Día 1 (Frontend)

**Fecha:** 30 de Noviembre de 2025
**Versión:** 1.0
**Objetivo:** Validar la correcta implementación del módulo de Autenticación, Navegación y Persistencia de Sesión.

---

## 1. Requisitos Previos

Antes de iniciar las pruebas, asegúrese de cumplir con lo siguiente:

1.  **Backend en Ejecución:**
    El backend debe estar corriendo localmente para responder a las peticiones de login.
    ```bash
    # En una terminal separada (carpeta backend)
    docker-compose up -d
    # O si corre localmente con Python
    uvicorn app.main:app --reload --port 8000
    ```

2.  **Entorno Frontend:**
    Tener Flutter instalado y configurado.
    ```bash
    flutter doctor
    ```

---

## 2. Ejecución del Proyecto

Para ejecutar la aplicación en modo de escritorio (macOS) o Web (Chrome), utilice el siguiente comando desde la carpeta `frontend`:

```bash
cd frontend
flutter run -d macos
# O para Chrome
flutter run -d chrome
```

---

## 3. Casos de Prueba (Test Cases)

### TC-01: Carga Inicial y Redirección (Splash Screen)
**Objetivo:** Verificar que la app inicia y decide correctamente a dónde navegar.
**Pasos:**
1.  Inicie la aplicación por primera vez (sin sesión previa).
2.  Observe la pantalla de carga (Splash) con el logo.
**Resultado Esperado:**
- La Splash Screen aparece por unos segundos.
- Al no haber token guardado, la app redirige automáticamente a la pantalla de **Login**.

### TC-02: Validación de Formulario (Campos Vacíos)
**Objetivo:** Verificar que no se envíen peticiones vacías.
**Pasos:**
1.  Estando en el Login, deje los campos "Correo Electrónico" y "Contraseña" vacíos.
2.  Presione el botón "Iniciar Sesión".
**Resultado Esperado:**
- No se realiza ninguna petición al backend.
- Aparecen mensajes de error debajo de los campos (ej. "El correo es requerido", "La contraseña es requerida").

### TC-03: Error de Autenticación (Credenciales Inválidas)
**Objetivo:** Verificar el manejo de errores del servidor.
**Pasos:**
1.  Ingrese un correo válido pero no registrado (ej. `test@error.com`).
2.  Ingrese cualquier contraseña.
3.  Presione "Iniciar Sesión".
**Resultado Esperado:**
- El botón muestra un indicador de carga (spinner).
- Aparece un mensaje flotante (SnackBar) indicando el error (ej. "Credenciales incorrectas" o "Usuario no encontrado").
- Permanece en la pantalla de Login.

### TC-04: Inicio de Sesión Exitoso
**Objetivo:** Verificar el flujo completo de autenticación.
**Pasos:**
1.  Ingrese las credenciales del administrador (creadas por defecto en el backend):
    - **Usuario:** `admin@conmaq.com`
    - **Contraseña:** `admin`
2.  Presione "Iniciar Sesión".
**Resultado Esperado:**
- El botón muestra carga.
- La app redirige a la pantalla **Home** (actualmente un placeholder que dice "Home Screen").
- No se muestran errores.

### TC-05: Persistencia de Sesión
**Objetivo:** Verificar que el usuario no necesita loguearse cada vez que abre la app.
**Pasos:**
1.  Complete el TC-04 (Login Exitoso).
2.  Cierre completamente la aplicación (Stop en la terminal o Cmd+Q).
3.  Vuelva a ejecutar `flutter run -d macos`.
**Resultado Esperado:**
- Aparece la Splash Screen brevemente.
- La app redirige **directamente al Home**, saltándose el Login.
- Esto confirma que el Token se guardó y recuperó correctamente del Secure Storage.

---

## 4. Solución de Problemas Comunes

- **Error de Conexión (SocketException):**
    - Asegúrese de que el backend esté corriendo en el puerto 8000.
    - Si usa Android Emulator, cambie `localhost` por `10.0.2.2` en `lib/core/constants/api_constants.dart`.
    - En macOS/iOS/Web, `localhost` debería funcionar correctamente.

- **Pantalla en Blanco:**
    - Verifique la consola de depuración para ver si hay errores de renderizado.
    - Ejecute `flutter clean` y `flutter pub get` si sospecha de caché corrupta.

---
*Fin del Manual de Pruebas*
