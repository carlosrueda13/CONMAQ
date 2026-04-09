# SECOP Connect Map

Plataforma web para transformar datos abiertos de contratación pública en oportunidades comerciales accionables.

## Qué hace

SECOP Connect Map toma contratos públicos de SECOP, los georreferencia en un mapa, extrae información útil del presupuesto oficial y del análisis de precios unitarios cuando esté disponible, identifica posibles listas de materiales, y conecta proveedores con contratistas para ofrecer bienes y servicios relevantes al contrato.

## Problema que resuelve

Hoy la información de contratación pública existe, pero está fragmentada, poco estructurada para uso comercial y difícil de explotar por proveedores de materiales, maquinaria y servicios. Los contratistas publican procesos; los proveedores llegan tarde, a ciegas o por referencias informales.

Esta plataforma busca:

- Detectar contratos y procesos con potencial comercial.
- Ubicarlos espacialmente para entender dónde está la demanda.
- Inferir necesidades de materiales y servicios a partir del presupuesto oficial.
- Generar un punto de encuentro entre contratistas y proveedores.

## Propuesta de valor

- Visualización geográfica de procesos SECOP.
- Enriquecimiento de datos con municipio, departamento y coordenadas.
- Extracción estructurada de ítems, cantidades y materiales desde anexos y presupuestos.
- Matching entre demanda del contrato y oferta de proveedores.
- Alertas tempranas para proveedores según categoría, zona y tipo de obra.

## Casos de uso

### Para proveedores
- Ver en mapa contratos activos por región.
- Filtrar por categoría: obra civil, vías, agua potable, edificaciones, interventoría, etc.
- Identificar materiales potenciales requeridos.
- Contactar contratistas con una oferta contextualizada.

### Para contratistas
- Recibir ofertas pertinentes según el tipo de proyecto.
- Encontrar proveedores cercanos por categoría de suministro.
- Reducir tiempos de búsqueda y cotización.

### Para analistas del mercado
- Monitorear inversión pública territorial.
- Analizar demanda agregada de materiales por zona.
- Detectar oportunidades antes de la adjudicación o en etapa contractual.

## Arquitectura propuesta

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Leaflet o Mapbox GL para visualización geográfica

### Backend
- Node.js con NestJS o Express
- API REST para contratos, ubicaciones, materiales y proveedores
- Jobs ETL para ingestión de SECOP y anexos

### Datos
- PostgreSQL + PostGIS
- Almacenamiento de archivos y anexos
- Cola de procesamiento para parsing de documentos

### IA / extracción documental
- Pipeline para leer presupuestos oficiales, APU y anexos técnicos
- Normalización de materiales y servicios
- Clasificación por categorías comerciales

## Módulos iniciales

1. Ingesta de datos abiertos SECOP.
2. Geocodificación por entidad, municipio y lugar de ejecución.
3. Mapa interactivo de contratos.
4. Parser de presupuesto oficial y anexos.
5. Motor de matching entre materiales/servicios y proveedores.
6. Dashboard de oportunidades.

## Estructura inicial del proyecto

```bash
/apps
  /web
  /api
/packages
  /ui
  /types
  /utils
/docs
```

## Roadmap MVP

### Fase 1
- Consumir datos abiertos de SECOP
- Mostrar contratos en mapa
- Filtros por región, estado, entidad y sector

### Fase 2
- Subir y procesar presupuesto oficial
- Extraer lista preliminar de materiales
- Perfil básico de proveedores

### Fase 3
- Matching automático
- Alertas y recomendaciones
- CRM liviano de contacto proveedor-contratista

## Riesgos y retos

- Calidad variable de los anexos publicados.
- Procesos con información incompleta o sin georreferenciación precisa.
- Presupuestos oficiales en PDF no estructurado.
- Necesidad de estandarizar nombres de materiales y servicios.

## Visión

Convertir la contratación pública abierta en una red comercial inteligente donde cada contrato genere visibilidad, competencia eficiente y oportunidades reales de negocio.

## Nombre provisional

SECOP Connect Map

## Siguientes pasos

1. Definir fuentes exactas de SECOP y campos mínimos del dataset.
2. Diseñar el esquema de base de datos.
3. Construir ETL inicial.
4. Levantar el frontend con mapa y filtros.
5. Integrar parser documental para presupuestos oficiales.

## Licencia

Pendiente.
