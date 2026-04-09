# Autonomous Operations Playbook

Este repositorio opera como una empresa de software semi-autónoma. Los agentes pueden producir código, abrir tareas, hacer handoffs y avanzar por fases incluso cuando faltan secretos o infraestructura externa.

## Regla central

Cuando falten secretos o fuentes externas, el sistema debe seguir funcionando en modo demo con datos de prueba, sin bloquear el desarrollo del frontend ni del backend.

## Fases operativas

### Fase 0 — Foundation
- Crear monorepo
- Definir agentes
- Definir backlog
- Crear issue templates
- Crear CI

### Fase 1 — Demo-first delivery
- Construir frontend con vistas reales
- Construir backend con endpoints reales
- Si faltan secretos, servir datos mock
- Permitir deploy de preview

### Fase 2 — Real data integration
- Conectar dataset de SECOP I y II desde Datos Abiertos
- Mapear columnas a contratos internos
- Normalizar ubicación
- Persistir en PostgreSQL

### Fase 3 — Supplier matching
- Registrar proveedores
- Clasificar materiales y servicios
- Generar matches

### Fase 4 — Production hardening
- Seguridad
- Observabilidad
- Performance
- Deploy estable

## Política de bloqueo

Ningún agente puede detener la entrega de valor por falta de secretos. Debe implementar un fallback explícito:

- Si no hay `SECOP_DATA_SOURCE`, usar `mockContracts`.
- Si no hay `DATABASE_URL`, usar repositorio en memoria o archivo local de prueba.
- Si no hay `MAPBOX_TOKEN`, usar lista/tablas y vista placeholder de mapa.

## Handoff mínimo obligatorio

Todo agente debe dejar:
- código
- README local
- criterios de aceptación
- ejemplo de uso
- TODOs claros para el siguiente agente

## Agentes que pueden trabajar ya

- AGENTE-1 PRODUCT-ARCHITECT
- AGENTE-3 BACKEND-PLATFORM
- AGENTE-4 FRONTEND-APP
- AGENTE-6 QA-RELIABILITY

## Agentes condicionados a secretos

- AGENTE-2 DATA-PIPELINE en modo real
- AGENTE-5 DEVOPS-DEPLOY para producción real
- AGENTE-7 SECURITY-COMPLIANCE completa

## Objetivo inmediato

Entregar una web navegable y desplegable que muestre contratos SECOP en modo demo y que conmute automáticamente a modo real cuando existan secretos y fuente de datos.
