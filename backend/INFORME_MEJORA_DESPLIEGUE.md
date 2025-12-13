# Informe de Mejora: Despliegue, DevOps y Observabilidad

**Fecha:** 2 de Diciembre de 2025
**Responsable:** GitHub Copilot (Agente de Infraestructura)
**Estado:** Implementado

---

## 1. Resumen Ejecutivo

En respuesta a la auditoría externa que calificó el factor "Despliegue y Observabilidad" con un **4/10**, se han implementado una serie de mejoras críticas para elevar la madurez del proyecto a un nivel estimado de **6-7/10**.

Las mejoras se centraron en tres pilares:
1.  **Integración Continua (CI):** Verificación automática de la construcción de contenedores.
2.  **Despliegue en Producción:** Configuración optimizada y segura para entornos productivos.
3.  **Observabilidad:** Implementación de logs estructurados y métricas en tiempo real.

---

## 2. Detalle de Mejoras Implementadas (Manual LEGO)

### 2.1. Integración Continua (CI) - Build Job

**Problema Detectado:** El pipeline de CI solo ejecutaba pruebas, pero no garantizaba que la aplicación pudiera empaquetarse correctamente en un contenedor Docker.

**Solución:** Se añadió un trabajo (`job`) de construcción (`build`) al flujo de trabajo de GitHub Actions.

**Archivo Modificado:** `.github/workflows/backend-ci.yml`

**Cómo Funciona:**
1.  Después de que pasan los tests (`needs: test-backend`), se inicia el job `build`.
2.  Ejecuta `docker build -t conmaq-backend:ci .`.
3.  Si el Dockerfile tiene errores o faltan archivos, el pipeline falla antes de intentar cualquier despliegue.

### 2.2. Configuración de Despliegue en Producción

**Problema Detectado:** Solo existía `docker-compose.yml` configurado para desarrollo (con `--reload`), inadecuado para producción.

**Solución:** Se creó un nuevo archivo de orquestación específico para producción.

**Archivo Creado:** `docker-compose.prod.yml`

**Características Clave:**
-   **Servidor de Aplicaciones:** Usa `gunicorn` con workers `uvicorn` para mayor rendimiento y estabilidad, en lugar de `uvicorn --reload`.
-   **Política de Reinicio:** `restart: always` para asegurar alta disponibilidad.
-   **Variables de Entorno:** Configurado para leer secretos y configuraciones desde el entorno del host, no hardcodeado.

**Instrucciones de Uso (LEGO):**
1.  Crear un archivo `.env.prod` en el servidor con las credenciales reales.
2.  Ejecutar:
    ```bash
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
    ```

### 2.3. Observabilidad - Logs Estructurados (JSON)

**Problema Detectado:** Los logs eran texto plano, difíciles de indexar y analizar en herramientas como ELK o Datadog.

**Solución:** Se implementó un formateador de logs en JSON.

**Archivo Creado:** `app/core/logging_config.py`
**Archivo Modificado:** `app/main.py`

**Resultado:**
Ahora los logs se ven así:
```json
{"timestamp": "2025-12-02 10:00:00", "level": "INFO", "message": "Application startup complete.", "module": "main", ...}
```
Esto permite filtrar por nivel, módulo o mensaje automáticamente.

### 2.4. Observabilidad - Métricas (Prometheus)

**Problema Detectado:** No había visibilidad sobre el rendimiento de la API (latencia, tasa de errores, tráfico).

**Solución:** Se instrumentó la aplicación para exponer métricas en formato Prometheus.

**Archivos Modificados/Creados:**
-   `requirements.txt`: Añadido `prometheus_client`.
-   `app/api/metrics_exporter.py`: Nuevo endpoint `/metrics`.
-   `app/main.py`: Middleware para contar peticiones HTTP automáticamente.

**Métricas Disponibles:**
-   `conmaq_requests_total`: Contador de peticiones con etiquetas `method`, `path` y `status`.

**Verificación:**
Acceder a `http://localhost:8000/metrics` para ver los datos en tiempo real.

---

## 3. Próximos Pasos (Roadmap)

Para alcanzar un nivel 9-10/10, se recomienda:
1.  **Despliegue Remoto:** Configurar un pipeline de CD que despliegue automáticamente a un entorno de Staging en AWS/Azure/Render.
2.  **Tracing Distribuido:** Implementar OpenTelemetry para rastrear peticiones a través de microservicios (si la arquitectura crece).
3.  **Alertas:** Configurar Prometheus Alertmanager para notificar caídas o tasas de error elevadas.

---
*Fin del Informe*
