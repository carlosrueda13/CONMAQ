# Manual de Configuración de Pasarela de Pagos (Stripe)

**Versión:** 1.0
**Fecha:** 26 de Noviembre de 2025
**Objetivo:** Guiar paso a paso en la creación y configuración de una cuenta de Stripe para recibir pagos en el sistema CONMAQ.

---

## 1. Introducción
Para procesar pagos de tarjetas de crédito/débito de manera segura, el sistema CONMAQ está diseñado para integrarse con **Stripe**. Stripe es una de las plataformas de pago más seguras y fáciles de usar del mundo.

**¿Qué necesitamos lograr?**
1.  Crear una cuenta en Stripe.
2.  Obtener las "Llaves" (API Keys) que conectan el sistema con Stripe.
3.  Configurar el sistema para saber cuándo un pago fue exitoso.

---

## 2. Creación de la Cuenta (Paso a Paso)

1.  **Ir al sitio web:**
    Abra su navegador y vaya a [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register).

2.  **Formulario de Registro:**
    *   **Email:** Ingrese el correo electrónico de la empresa.
    *   **Nombre completo:** Nombre del administrador.
    *   **Contraseña:** Cree una contraseña segura.
    *   Haga clic en **"Create account"**.

3.  **Verificación de Email:**
    Revise su bandeja de entrada y haga clic en el enlace de verificación que Stripe le envió.

4.  **Activar Pagos (Opcional para Pruebas):**
    *   Para empezar a desarrollar, **NO** necesita activar la cuenta con datos bancarios reales todavía.
    *   Asegúrese de que el interruptor **"Test Mode"** (Modo de Prueba) en la parte superior derecha del Dashboard esté **ACTIVADO** (Color Naranja).

---

## 3. Obtención de las API Keys

Las API Keys son como el "Usuario" y "Contraseña" que el sistema CONMAQ usa para hablar con Stripe.

1.  En el Dashboard de Stripe, vaya a la pestaña **"Developers"** (Desarrolladores) en la esquina superior derecha.
2.  En el menú de la izquierda, haga clic en **"API keys"**.
3.  Verá dos claves en el recuadro "Standard keys":
    *   **Publishable key (Clave pública):** Empieza con `pk_test_...`.
        *   *Esta clave se usa en la Aplicación Móvil/Web.*
    *   **Secret key (Clave secreta):** Empieza con `sk_test_...`.
        *   Haga clic en "Reveal test key" para verla.
        *   **IMPORTANTE:** Copie esta clave y guárdela en un lugar seguro. *Nunca la comparta con nadie fuera del equipo técnico.*

---

## 4. Configuración en el Sistema CONMAQ

Una vez tenga las claves, debe entregarlas al equipo de desarrollo o configurarlas en el servidor.

### 4.1 Variables de Entorno
El sistema backend necesita estas claves en su archivo de configuración (`.env`):

```bash
# Archivo .env en el servidor backend
STRIPE_API_KEY=sk_test_51Mz... (Su Secret Key)
STRIPE_WEBHOOK_SECRET=whsec_... (Ver sección 5)
```

### 4.2 Configuración Frontend
La aplicación móvil necesita la clave pública:

```dart
// Configuración en Flutter
const stripePublishableKey = "pk_test_51Mz...";
```

---

## 5. Configuración de Webhooks (Avanzado)

Los "Webhooks" son la forma en que Stripe le avisa al sistema: *"¡Hey! El pago de $100 USD fue exitoso"*.

1.  En el Dashboard de Stripe (Developers), vaya a **"Webhooks"** en el menú izquierdo.
2.  Haga clic en **"Add endpoint"**.
3.  **Endpoint URL:** Ingrese la URL de su servidor.
    *   *Ejemplo:* `https://api.conmaq.com/api/v1/payments/webhook`
4.  **Events to send:** Haga clic en "Select events" y busque:
    *   `payment_intent.succeeded`
    *   `payment_intent.payment_failed`
5.  Haga clic en **"Add endpoint"**.
6.  **Signing Secret:**
    *   Una vez creado, verá una sección llamada "Signing secret".
    *   Haga clic en "Reveal".
    *   Copie este valor (empieza con `whsec_...`).
    *   Este es el valor para `STRIPE_WEBHOOK_SECRET` en el paso 4.1.

---

## 6. Cómo Probar Pagos (Test Mode)

Mientras el sistema esté en "Test Mode", **NO** use su tarjeta de crédito real. Use las tarjetas de prueba de Stripe:

| Tipo de Tarjeta | Número de Tarjeta | Fecha Exp | CVC |
| :--- | :--- | :--- | :--- |
| **Visa (Éxito)** | `4242 4242 4242 4242` | Cualquiera futura | Cualquiera |
| **Mastercard** | `5555 5555 5555 4444` | Cualquiera futura | Cualquiera |
| **Fallo Genérico** | `4000 0000 0000 0002` | Cualquiera futura | Cualquiera |

**Flujo de Prueba:**
1.  Abra la App CONMAQ.
2.  Gane una subasta o cree una reserva.
3.  Vaya a "Pagar".
4.  Ingrese los datos de la tarjeta Visa de prueba (`4242...`).
5.  El sistema debería confirmar el pago y cambiar el estado de la reserva a `confirmed`.

---

## 7. Pasar a Producción (Go Live)

Cuando esté listo para recibir dinero real:
1.  En el Dashboard, apague el interruptor **"Test Mode"**.
2.  Complete el formulario de activación (Datos de la empresa, cuenta bancaria para recibir depósitos).
3.  Obtenga las nuevas **API Keys de Producción** (`pk_live_...` y `sk_live_...`).
4.  Reemplace las claves en el servidor y la app.

¡Listo! Su sistema de pagos está configurado.
