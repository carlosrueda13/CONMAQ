# Sistema de Subagentes para SECOP Connect Map

Este documento define un árbol de subagentes especializados para construir, validar, desplegar y operar la plataforma de forma altamente autónoma.

## Objetivo

Coordinar trabajo paralelo sobre producto, datos, backend, frontend, parsing documental, matching comercial, calidad, seguridad y deploy hasta alcanzar una web completamente funcional en producción.

## Principios operativos

1. Cada subagente tiene un dominio claro, inputs definidos, outputs obligatorios y criterios de aceptación.
2. Ningún subagente modifica áreas fuera de su dominio sin abrir una tarea de handoff.
3. Todo cambio relevante debe quedar reflejado en documentación, pruebas y criterios de despliegue.
4. Los agentes trabajan por ramas, con PRs pequeños y trazables.
5. Se prioriza autonomía, pero con contratos claros entre agentes.

## Árbol de subagentes

```text
AGENTE-0 ORCHESTRATOR
├── AGENTE-1 PRODUCT-ARCHITECT
│   ├── AGENTE-1.1 UX-FLOWS
│   └── AGENTE-1.2 DOMAIN-MODELER
├── AGENTE-2 DATA-PIPELINE
│   ├── AGENTE-2.1 SECOP-INGESTOR
│   ├── AGENTE-2.2 GEO-ENRICHMENT
│   └── AGENTE-2.3 DOCUMENT-PARSER
├── AGENTE-3 BACKEND-PLATFORM
│   ├── AGENTE-3.1 API-DESIGN
│   ├── AGENTE-3.2 MATCHING-ENGINE
│   └── AGENTE-3.3 AUTH-AND-ROLES
├── AGENTE-4 FRONTEND-APP
│   ├── AGENTE-4.1 MAP-EXPERIENCE
│   ├── AGENTE-4.2 CONTRACT-DETAIL
│   └── AGENTE-4.3 SUPPLIER-PORTAL
├── AGENTE-5 DEVOPS-DEPLOY
│   ├── AGENTE-5.1 CI-CD
│   ├── AGENTE-5.2 INFRA-DB
│   └── AGENTE-5.3 OBSERVABILITY
├── AGENTE-6 QA-RELIABILITY
│   ├── AGENTE-6.1 TEST-AUTOMATION
│   ├── AGENTE-6.2 E2E-VALIDATION
│   └── AGENTE-6.3 PERFORMANCE
└── AGENTE-7 SECURITY-COMPLIANCE
    ├── AGENTE-7.1 DATA-GOVERNANCE
    └── AGENTE-7.2 APPSEC
```

## Flujo maestro

1. AGENTE-0 descompone objetivos en épicas y tareas.
2. AGENTE-1 define dominio, historias, UX y criterios.
3. AGENTE-2 produce datasets confiables y documentos parseados.
4. AGENTE-3 expone servicios y reglas de negocio.
5. AGENTE-4 consume APIs y construye la experiencia web.
6. AGENTE-5 despliega entornos y automatiza delivery.
7. AGENTE-6 valida funcionamiento integral.
8. AGENTE-7 bloquea riesgos legales, de seguridad y exposición de datos.

## Definición de terminado global

El proyecto se considera funcional cuando cumple:

- Mapa interactivo con contratos SECOP cargados desde fuente reproducible.
- Filtros por ubicación, estado, sector, entidad y presupuesto.
- Vista detalle por contrato.
- Ingesta documental reproducible.
- Extracción preliminar de materiales y servicios desde anexos.
- Registro y perfil de proveedores.
- Matching básico contrato ↔ proveedor.
- Backend desplegado.
- Frontend desplegado.
- Base de datos persistente.
- Pipeline CI/CD operativo.
- Suite mínima de pruebas.
- Observabilidad y logs.

## Método de trabajo recomendado

- Trunk-based con ramas cortas por agente.
- PRs pequeños por capacidad.
- Checklists de aceptación por carpeta.
- Issues etiquetados por agente y fase.

## Convención de ramas

- feat/a1-domain-model
- feat/a21-secop-ingestor
- feat/a23-document-parser
- feat/a31-api-contracts
- feat/a41-map-ui
- feat/a51-cicd
- fix/a61-e2e-bugs
- chore/a71-security-hardening

## Convención de handoff

Todo agente debe emitir un handoff cuando:

- crea un nuevo contrato de datos
- agrega un endpoint consumible por otro agente
- modifica el esquema de base de datos
- cambia variables de entorno
- introduce una dependencia crítica

Formato de handoff:

```md
## Handoff
Origen: AGENTE-X
Destino: AGENTE-Y
Motivo: ...
Entradas nuevas: ...
Cambios incompatibles: ...
Pruebas ejecutadas: ...
Pendientes: ...
```
