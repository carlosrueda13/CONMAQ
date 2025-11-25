# Guía de Pruebas Manuales - Día 2 (Motor de Subastas y Notificaciones)

Esta guía detalla los pasos para validar manualmente las funcionalidades implementadas durante el Día 2.

**Pre-requisitos:**
1.  El backend debe estar corriendo (`uvicorn app.main:app --reload`).
2.  Acceder a la documentación interactiva: `http://localhost:8000/docs`.
3.  Tener al menos 2 usuarios creados (Usuario A y Usuario B) para simular competencia.

---

## 1. Preparación del Entorno (Datos Base)

Antes de probar las subastas, necesitamos una máquina y un slot de tiempo disponible.

1.  **Login como Admin** (si no tienes token):
    *   `POST /auth/login/access-token`
    *   User: `admin@conmaq.com`, Pass: `admin`
    *   *Copia el `access_token` y autorízate en el botón "Authorize" (candado).*

2.  **Crear una Máquina**:
    *   `POST /machines/`
    *   JSON:
        ```json
        {
          "name": "Excavadora de Prueba D2",
          "serial_number": "TEST-D2-001",
          "price_base_per_hour": 100.0,
          "specs": {},
          "location_lat": 4.6,
          "location_lng": -74.0
        }
        ```
    *   *Anota el `id` de la máquina creada (ej. `1`).*

3.  **Generar Disponibilidad**:
    *   `POST /machines/{id}/availability/generate`
    *   `id`: `1` (o el que anotaste).
    *   `days`: `1`.
    *   *Response 200 OK.*

4.  **Obtener un Slot ID**:
    *   `GET /machines/{id}/availability`
    *   Busca el `id` del primer slot disponible en la lista.
    *   *Anota este `slot_id` (ej. `1`).*

---

## 2. Prueba de Watchlist (Lista de Seguimiento)

**Actor:** Usuario A (puedes usar el mismo Admin o crear uno nuevo).

1.  **Agregar a Watchlist**:
    *   `POST /watchlist/toggle`
    *   JSON: `{"machine_id": 1}`
    *   **Resultado Esperado:** JSON con `{"status": "added", "machine_id": 1}`.

2.  **Verificar Lista**:
    *   `GET /watchlist/`
    *   **Resultado Esperado:** Una lista que contiene la máquina con ID 1.

3.  **Quitar de Watchlist**:
    *   `POST /watchlist/toggle` (Mismo endpoint, misma data).
    *   JSON: `{"machine_id": 1}`
    *   **Resultado Esperado:** JSON con `{"status": "removed", ...}`.

---

## 3. Prueba de Motor de Subastas (Bidding War)

Para esta prueba, simularé dos usuarios. Si estás probando solo, tendrás que loguearte y desloguearte, o usar dos navegadores/pestañas de incógnito.

**Escenario:**
*   Precio Base: $100.
*   Incremento Mínimo: $10.

### Paso 3.1: Usuario A oferta (Primera Oferta)
1.  **Login como Usuario A**.
2.  **Realizar Oferta**:
    *   `POST /offers/`
    *   JSON:
        ```json
        {
          "slot_id": 1,
          "max_bid": 150.0
        }
        ```
    *   **Resultado Esperado:**
        *   `status`: "success"
        *   `current_price`: 100.0 (Precio base, ya que nadie más ha ofertado).
        *   `winner_id`: ID del Usuario A.

### Paso 3.2: Usuario B intenta superar (Proxy Bidding)
1.  **Login como Usuario B**.
2.  **Realizar Oferta (Menor al máximo de A)**:
    *   `POST /offers/`
    *   JSON:
        ```json
        {
          "slot_id": 1,
          "max_bid": 120.0
        }
        ```
    *   **Resultado Esperado:**
        *   `status`: "success"
        *   `current_price`: 130.0 (120 del Usuario B + 10 de incremento).
        *   **Importante:** El `winner_id` **sigue siendo el Usuario A**, porque su máximo era 150. El sistema ofertó automáticamente por A para defender su posición.

### Paso 3.3: Usuario B gana la subasta
1.  **Login como Usuario B** (si no lo estás ya).
2.  **Realizar Oferta Ganadora**:
    *   `POST /offers/`
    *   JSON:
        ```json
        {
          "slot_id": 1,
          "max_bid": 200.0
        }
        ```
    *   **Resultado Esperado:**
        *   `current_price`: 160.0 (150 del Usuario A + 10 incremento).
        *   `winner_id`: ID del Usuario B.

---

## 4. Prueba de Notificaciones

Al completar el **Paso 3.3**, el Usuario A fue superado ("Outbid"). El sistema debió generarle una notificación.

1.  **Login como Usuario A**.
2.  **Ver Notificaciones**:
    *   `GET /notifications/`
    *   **Resultado Esperado:**
        *   Una lista con al menos un objeto.
        *   `type`: "outbid"
        *   `title`: "Has sido superado"
        *   `is_read`: false
3.  **Marcar como Leída**:
    *   Copia el `id` de la notificación.
    *   `PUT /notifications/{id}/read`
    *   **Resultado Esperado:** `is_read`: true.

---

## 5. Verificación de Historial
1.  **Ver mis ofertas**:
    *   `GET /offers/my-offers`
    *   Deberías ver el historial de tus intentos y sus estados (`winning`, `outbid`).
