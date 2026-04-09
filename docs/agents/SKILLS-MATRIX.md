# Matriz de Skills por Subagente

Este documento enumera las capacidades necesarias por subagente, qué queda ya definido dentro del repositorio y qué falta para poder operar con autonomía alta.

## Estado general

- Estado actual: preparado a nivel de diseño y coordinación.
- Estado técnico real: aún no existe app funcional, pipeline, base de datos ni CI/CD.
- Conclusión: los agentes pueden empezar a producir entregables de arquitectura, contratos de datos, estructura de código y documentación; todavía no pueden ejecutar un ciclo completo de build → test → deploy sin instalar stack y secretos.

## AGENTE-0 ORCHESTRATOR

### Skills necesarias
- Planeación de épicas
- Descomposición en tareas
- Gestión de dependencias
- Definición de criterios de aceptación
- Gestión de handoffs

### Ya disponible
- Árbol de agentes
- Convenciones de ramas
- Convención de handoff
- Definición de terminado global

### Falta
- Backlog formal en GitHub Issues
- Templates de issues y PRs
- Tablero de proyecto

## AGENTE-1 PRODUCT-ARCHITECT

### Skills necesarias
- Product discovery
- Diseño de flujos
- Definición de historias de usuario
- Modelado de dominio
- Diseño funcional del marketplace

### Ya disponible
- Visión del producto
- Módulos del MVP
- Roadmap por fases

### Falta
- User journeys detallados
- Wireframes
- Modelo de dominio formal
- Especificación funcional del matching

## AGENTE-2 DATA-PIPELINE

### Skills necesarias
- Consumo de APIs y datasets abiertos
- ETL
- Parsing documental
- OCR opcional
- Normalización de materiales
- Geocodificación
- PostGIS

### Ya disponible
- Objetivo funcional del pipeline
- Módulos y outputs esperados

### Falta
- Fuente concreta de SECOP definida
- Scripts ETL
- Conectores de ingesta
- Estrategia de parsing PDF/Excel
- Diccionario de materiales
- Persistencia en base de datos

## AGENTE-3 BACKEND-PLATFORM

### Skills necesarias
- NestJS o Express
- Diseño REST API
- PostgreSQL
- PostGIS
- Auth
- Jobs asíncronos
- Reglas de matching

### Ya disponible
- Lista conceptual de endpoints
- Separación de dominios funcionales

### Falta
- Proyecto backend inicializado
- ORM
- Esquema de base de datos
- Endpoints implementados
- Sistema de autenticación
- Workers de procesamiento

## AGENTE-4 FRONTEND-APP

### Skills necesarias
- Next.js
- React
- TypeScript
- Tailwind
- Mapbox o Leaflet
- Manejo de estado
- Formularios y tablas

### Ya disponible
- Módulos de interfaz definidos
- Flujo principal implícito

### Falta
- Proyecto frontend inicializado
- Diseño UI base
- Mapa renderizado
- Filtros
- Vistas de detalle
- Portal de proveedor

## AGENTE-5 DEVOPS-DEPLOY

### Skills necesarias
- GitHub Actions
- Vercel o Netlify
- Railway / Render / Fly.io
- PostgreSQL administrado
- Variables de entorno
- Monitoreo

### Ya disponible
- Objetivo de deploy definido

### Falta
- Workflow CI
- Workflow CD
- Cuentas conectadas de hosting
- Secretos del repositorio
- Base de datos aprovisionada
- Dominio y configuración DNS opcional

## AGENTE-6 QA-RELIABILITY

### Skills necesarias
- Jest
- Playwright
- Testing API
- Performance testing
- Smoke tests

### Ya disponible
- Objetivo de validación definido

### Falta
- Framework de tests instalado
- Casos de prueba
- Fixtures de datos
- Pipeline de pruebas

## AGENTE-7 SECURITY-COMPLIANCE

### Skills necesarias
- Hardening de API
- Control de secretos
- Escaneo de dependencias
- Protección de datos
- Rate limiting
- Validación de inputs

### Ya disponible
- Rol de seguridad definido

### Falta
- Política de seguridad
- Secret scanning
- Dependabot o equivalente
- Middleware de seguridad
- Revisión legal de uso de datos y documentos

## Skills transversales mínimas para arrancar de verdad

1. Monorepo Node.js + TypeScript
2. Gestor de paquetes (pnpm recomendado)
3. Frontend Next.js
4. Backend NestJS
5. PostgreSQL + PostGIS
6. ORM (Prisma o Drizzle)
7. Tailwind CSS
8. Mapbox GL o Leaflet
9. ETL para SECOP
10. Parser documental para PDF/Excel
11. GitHub Actions
12. Vercel / Railway / Supabase o equivalente
13. Jest + Playwright
14. ESLint + Prettier
15. Variables de entorno y gestión de secretos

## Qué significa “instalarlas” en este contexto

Dentro de GitHub, lo que sí puede dejarse instalado ahora mismo es:

- estructura de carpetas
- archivos de configuración
- prompts operativos para agentes
- plantillas de trabajo
- workflows YAML
- README técnicos
- contratos de datos

Lo que no puede quedar realmente instalado solo desde GitHub sin servicios externos es:

- base de datos activa
- despliegue en Vercel o Railway
- secretos del repositorio
- claves de proveedores externos
- dominios y DNS

## Gate de arranque

Los agentes pueden empezar a trabajar en serio cuando existan al menos estos activos:

- `/apps/web`
- `/apps/api`
- `/packages/types`
- `/packages/utils`
- `pnpm-workspace.yaml`
- `package.json` raíz
- `.github/workflows/ci.yml`
- `.env.example`
- esquema inicial de base de datos
- decisiones de stack congeladas

## Recomendación inmediata

Siguiente iteración: crear el esqueleto técnico mínimo del monorepo y la carpeta `.github/` con workflows, templates y prompts para agentes. Ese paso habilita trabajo paralelo real.
