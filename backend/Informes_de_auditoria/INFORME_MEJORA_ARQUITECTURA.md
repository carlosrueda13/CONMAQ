# Informe de Mejora de Arquitectura

## 1. Introducción

Este documento detalla las mejoras arquitectónicas implementadas en el backend del sistema, siguiendo las recomendaciones de la auditoría externa. El objetivo principal ha sido desacoplar la lógica de negocio de la capa de transporte (API/FastAPI) mediante la introducción de una **Capa de Servicios de Dominio**.

Imagina que nuestro sistema es una construcción de LEGO. Antes, las piezas de "lógica" estaban pegadas con pegamento a las piezas de "conexión" (API). Si queríamos cambiar la forma de conexión, teníamos que romper la lógica. Ahora, hemos separado las piezas. Tenemos bloques de lógica puros (Servicios) que pueden conectarse a cualquier interfaz (API REST, CLI, GraphQL, etc.) sin cambios.

## 2. Cambios Realizados

### 2.1. Introducción de la Capa de Servicios (`app/services`)

Se ha creado un nuevo directorio `app/services` que actúa como el núcleo de la lógica de negocio. Cada módulo en este directorio corresponde a un dominio del negocio.

**Estructura Anterior:**
```
app/
  api/
    endpoints/
      users.py (Contenía lógica de validación, creación, ORM, etc.)
      machines.py
      ...
```

**Nueva Estructura:**
```
app/
  api/
    endpoints/
      users.py (Solo recibe HTTP, llama al servicio y devuelve respuesta)
  services/
    user.py (Contiene toda la lógica de negocio pura)
    machine.py
    booking.py
    offer.py
    ...
```

### 2.2. Refactorización por Dominio

Se han refactorizado los siguientes dominios para seguir el patrón **Controller -> Service -> Model**:

1.  **Watchlist (`app/services/watchlist.py`)**: Lógica para gestionar la lista de seguimiento de máquinas.
2.  **Notifications (`app/services/notifications.py`)**: Lógica para recuperar y marcar notificaciones.
3.  **Metrics (`app/services/metrics.py`)**: Cálculos de métricas financieras y operativas.
4.  **Bookings (`app/services/booking.py`)**: Creación de reservas, check-in, check-out y gestión de estados.
5.  **Users (`app/services/user.py`)**: Creación y recuperación de usuarios.
6.  **Machines (`app/services/machine.py`)**: CRUD de máquinas y generación de disponibilidad.
7.  **Offers (`app/services/offer.py`)**: Lógica compleja de subastas (Proxy Bidding) y gestión de ofertas.
8.  **Payments (`app/services/payment.py`)**: Integración con pasarela de pagos (simulada) e historial.

### 2.3. Beneficios Obtenidos

*   **Testabilidad**: Ahora es posible probar la lógica de negocio (`app/services`) sin necesidad de levantar un servidor HTTP o simular peticiones API.
*   **Reusabilidad**: La lógica de los servicios puede ser llamada desde tareas en segundo plano (Celery), scripts de administración o diferentes interfaces.
*   **Mantenibilidad**: El código es más limpio y fácil de leer. Los controladores API son extremadamente delgados.
*   **Preparación para Hexagonal**: Este es el primer paso hacia una Arquitectura Hexagonal completa. Los servicios actuales pueden evolucionar fácilmente hacia "Casos de Uso" o "Interactors".

## 3. Guía de Uso para Desarrolladores ("Instrucciones de Montaje")

### ¿Cómo añadir una nueva funcionalidad?

1.  **Identifica el Dominio**: ¿A qué parte del negocio pertenece? (Ej. "Gestión de Inventario").
2.  **Crea/Edita el Servicio**:
    *   Ve a `app/services/`.
    *   Si es un dominio nuevo, crea `inventario.py`.
    *   Define una función pura que reciba los datos necesarios (Pydantic schemas o tipos básicos) y la sesión de DB.
    *   Implementa la lógica: validaciones, cálculos, llamadas a DB.
    *   Retorna el modelo ORM o los datos procesados.
3.  **Crea/Edita el Endpoint**:
    *   Ve a `app/api/v1/endpoints/`.
    *   Inyecta la dependencia de base de datos (`db: Session`).
    *   Llama a la función del servicio: `resultado = inventario_service.crear_item(db, datos)`.
    *   Maneja excepciones de negocio y conviértelas a `HTTPException` si es necesario.
    *   Retorna el resultado.

### Ejemplo: Crear una Máquina

**Antes (en endpoint):**
```python
# app/api/v1/endpoints/machines.py
def create_machine(machine_in, db):
    # ... mucha lógica de validación ...
    db_obj = Machine(...)
    db.add(db_obj)
    db.commit()
    return db_obj
```

**Ahora:**

**1. Servicio (`app/services/machine.py`):**
```python
def create_machine(db: Session, machine_in: MachineCreate) -> Machine:
    # Lógica pura
    db_obj = Machine(...)
    db.add(db_obj)
    db.commit()
    return db_obj
```

**2. Endpoint (`app/api/v1/endpoints/machines.py`):**
```python
def create_machine(machine_in, db):
    return machine_service.create_machine(db, machine_in)
```

## 4. Próximos Pasos

*   **Interfaces (Protocolos)**: Definir interfaces abstractas para los repositorios de datos para desacoplar totalmente de SQLAlchemy (Paso final a Hexagonal).
*   **Inyección de Dependencias**: Usar un contenedor de inyección de dependencias más robusto si la complejidad crece.
*   **Tests Unitarios**: Crear tests unitarios específicos para cada función en `app/services/` para asegurar la cobertura de la lógica de negocio.

---
*Generado por el Equipo de Arquitectura (AI Agent)*
