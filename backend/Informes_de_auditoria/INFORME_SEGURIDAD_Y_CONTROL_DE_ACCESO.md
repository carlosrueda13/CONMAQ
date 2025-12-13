# Informe de Auditoría – Seguridad y Control de Acceso (Backend CONMAQ)

## 1. Calificación

**Calificación global en “Seguridad y Control de Acceso”: _7 / 10_**

---

## 2. Explicación de la calificación

### 2.1. Resumen

El backend de CONMAQ presenta una **base de seguridad sólida a nivel de aplicación**, especialmente para un MVP:

- Autenticación con **JWT** (via `PyJWT` y `passlib[bcrypt]`).
- Control de acceso por **roles** (`role`, `is_superuser`) y dependencias específicas (`get_current_active_admin`, `get_current_active_superuser`).
- **Rate limiting** configurado vía `slowapi` y **Redis**.
- Esquemas Pydantic detallados, que aportan **validación estructural de entrada**.
- Contraseñas hasheadas con **bcrypt**.
- Documentación explícita en el PRD y en el Manual Técnico relacionada con OWASP, rate limiting, CORS, headers de seguridad, etc.

Estos elementos encajan claramente con la banda **7–9** de la rúbrica:

> “Autenticación segura con mecanismos estándar (OAuth2 con expiración de tokens, JWT firmado) y autorización por roles/claims (…) Validación completa de datos de entrada según esquemas (…) Uso de cifrado en reposo (contraseñas hasheadas) (…) logs de auditoría, limitación de tasa, escaneo de seguridad programado”.

Sin embargo, aún hay varios aspectos críticos que impiden llegar a 9–10:

- El despliegue Docker actual usa **Uvicorn en modo dev** con `--reload` y sin configuración explícita de **HTTPS/TLS**, HSTS ni reverse proxy seguro.
- Falta evidencia de:
  - WAF/gateway API real en front (Nginx, Traefik, Kong, etc.).
  - CSRF/XSS mitigados explícitamente (por ejemplo, en endpoints de frontend que pudieran convivir con browsers).
  - Políticas concretas de **rotación de llaves** (`SECRET_KEY`, claves de Stripe), ni de gestión centralizada de secretos.
  - Logs de auditoría de seguridad estructurados y procesos de **escaneo de vulnerabilidades** automatizado (SAST/DAST).

Por esto, la calificación se fija en **7/10**: seguridad **buena y basada en estándares**, pero todavía sin todas las capas “enterprise/bancarias” que pide el 9–10.

---

### 2.2. Fortalezas de seguridad y control de acceso

#### 2.2.1. Autenticación y manejo de credenciales

**Evidencias:**

- `requirements.txt` incluye:

  ```text
  PyJWT>=2.8.0
  passlib[bcrypt]>=1.7.4
  python-multipart>=0.0.6
  email-validator>=2.1.0.post1
  ```

- `DOCUMENTACION_TECNICA.md` describe:

  - `app/core/security.py` con:
    - `create_access_token(subject, expires_delta)` usando `jwt.encode` con `SECRET_KEY` y algoritmo `HS256`.
    - `verify_password` usando `passlib` (bcrypt).
    - `get_password_hash`.

- `app/core/config.py` (descrito en la doc):

  - `SECRET_KEY`
  - `ALGORITHM` (HS256)
  - `ACCESS_TOKEN_EXPIRE_MINUTES`

- `auth.py` (descrita en DOCUMENTACION_TECNICA):

  - Endpoint `POST /api/v1/auth/login/access-token`:
    - Valida usuario y contraseña.
    - Rechaza usuarios inactivos.
    - Devuelve `Token` con `access_token` + `token_type`.

**Conclusión:**

- Se está usando un stack estándar y correcto para APIs modernas:
  - JWT firmados.
  - Contraseñas hasheadas con bcrypt (no en claro).
  - Expiración de tokens configurada.

Esto es claramente **≥5–6** y encaja en la franja **7–9**.

#### 2.2.2. Autorización granular basada en roles y dependencias

**Evidencias:**

- `DOCUMENTACION_TECNICA.md` sección 8:

  - `app/api/deps.py` define:

    - `get_current_user` → decodifica JWT, obtiene usuario de DB.
    - `get_current_active_user` → verifica `is_active`.
    - `get_current_active_superuser` → verifica `is_superuser`.
    - `get_current_active_admin` → verifica `user.role == "admin"` o superuser.

- Ejemplos de uso en endpoints:

  - `metrics.py`:

    ```python
    @router.get("/financial")
    def get_financial_metrics(
        db: Session = Depends(deps.get_db),
        current_user: Any = Depends(deps.get_current_active_admin),
    ):
        ...
    ```

  - `machines.create_machine`: solo superusuario.
  - Endpoints de notificaciones, watchlist, offers:
    - Usan `current_user: User = Depends(deps.get_current_active_user)`.

**Conclusión:**

- Existe **RBAC** (Role-Based Access Control) razonablemente bien aplicado:
  - Rutas de administración (métricas, CRUD máquinas) restringidas.
  - Rutas de usuario autenticado restringidas a `get_current_active_user`.
- Esto supera la seguridad “básica” 2–4 en la rúbrica y entra en **seguridad sólida 7–9**.

#### 2.2.3. Rate limiting y protección contra abuso básico

**Evidencias:**

- `requirements.txt`: `slowapi>=0.1.9`, `redis>=5.0.1`.
- `docker-compose.yml` expone `redis`.
- `app/main.py`:

  ```python
  from slowapi import _rate_limit_exceeded_handler
  from slowapi.errors import RateLimitExceeded
  from app.core.limiter import limiter

  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  ```

- `users.py`:

  ```python
  from app.core.limiter import limiter

  @router.post("/", response_model=UserSchema)
  @limiter.limit("5/minute")
  def create_user(...):
      ...
  ```

- `DOCUMENTACION_TECNICA.md` (sección seguridad):

  - Detalla rate limiting:
    - Login: 5/min.
    - Registro: 3/min.
    - Ofertas: 10/min.

**Conclusión:**

- Se ha implementado **limitación de tasa** en endpoints críticos (auth, ofertas).
- Esto mitiga:
  - Fuerza bruta de login/registro.
  - Abuso de endpoints de bidding.
- Encaja con los requisitos de seguridad 7–9 (“rate limiting para evitar DoS”).

#### 2.2.4. Validación de entrada y protección básica ante inyecciones

**Evidencias:**

- `app/schemas/*.py` descritos en DOCUMENTACION_TECNICA:

  - `UserCreate`, `MachineCreate`, `OfferCreate`, `BookingCheckIn`, etc.
  - Tipos fuertes: `EmailStr`, `float`, `int`, `JSON`, etc.

- Uso consistente de Pydantic en endpoints:

  - Ejemplo `users.create_user`:

    ```python
    def create_user(
        *,
        request: Request,
        db: Session = Depends(deps.get_db),
        user_in: UserCreate,
    ) -> Any:
        ...
    ```

- Acceso a DB vía SQLAlchemy ORM (en vez de construir SQL a mano).
- Alembic env:

  - Usa `settings.DATABASE_URL` y `engine_from_config` con pool gestionado.

**Conclusión:**

- Se aplican **esquemas de validación estrictos** (Pydantic) que filtran entradas malformadas y tipos incorrectos.
- El uso de ORM mitiga (no elimina por completo) riesgos de SQL Injection al evitar concatenación de strings.
- Esto cumple con el criterio **5–9** en la rúbrica.

#### 2.2.5. Contraseñas y datos críticos

**Evidencias:**

- `User` en `DOCUMENTACION_TECNICA.md`:

  - `hashed_password` (no `password`).
  - `is_active`, `is_superuser`.

- `Payment` y `Transaction`:

  - No almacenan datos de tarjeta, solo:
    - `provider_transaction_id`
    - `amount`, `currency`, `status`, `type`.

- `MANUAL_CONFIGURACION_PAGOS.md` y `PRD_agendamiento.md`:

  - Enfatizan que:
    - No se deben almacenar PAN/CVV.
    - Stripe se usa para tokenización.

**Conclusión:**

- **Contraseñas hasheadas** correctamente (bcrypt).
- Datos de tarjetas **no se almacenan**, solo IDs de proveedor.
- Muy alineado con buenas prácticas PCI y OWASP.

---

### 2.3. Principales debilidades y brechas

#### 2.3.1. Ausencia de HTTPS/TLS configurado en el entorno de ejemplo

- `docker-compose.yml` expone `web` en `http://localhost:8000`, sin TLS.
- `Dockerfile` lanza Uvicorn directamente, sin reverse proxy TLS (Nginx/Traefik/Envoy).
- PRD menciona HTTPS como requerimiento no funcional, pero no hay manifests concretos ni documentación de cómo hacer el terminate TLS.

**Impacto:**

- En ambiente de desarrollo está bien.
- Pero en producción, **sin un plan claro y documentado de TLS**, los tokens JWT y credenciales podrían circular en texto claro si alguien despliega “tal cual”.

En la rúbrica, para 7–9 se asume:

> “Todas las conexiones forzadas a HTTPS y se configuran HSTS…”

Actualmente, eso está en intención (PRD), pero no en configuración.

#### 2.3.2. CORS y headers de seguridad no endurecidos en producción

- `app/main.py`:

  ```python
  origins = [
      "http://localhost",
      "http://localhost:3000",
      "http://localhost:8080",
  ]

  app.add_middleware(
      CORSMiddleware,
      allow_origins=origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- Comentario: “In production, replace [\"*\"] with specific origins”.

**Observación:**

- Para desarrollo, la configuración está bien.
- Para producción:
  - No hay un `settings.CORS_ORIGINS` externo con lista controlada.
  - `allow_methods=["*"]` y `allow_headers=["*"]` son muy permisivos si no se filtra por origen estricto.
  - No se ven referencias a middleware de headers de seguridad (HSTS, CSP, etc.) implementados.

#### 2.3.3. Gestión de secretos y rotación

- `app/core/config.py`:

  ```python
  SECRET_KEY: str = "changethis_secret_key_for_dev"
  ```

- `docker-compose.yml`:

  ```yaml
  environment:
    - SECRET_KEY=changethis_secret_key_for_dev
  ```

**Riesgos:**

- Valor por defecto embebido en código (válido para dev).
- Sin documentación de:
  - Rotación de `SECRET_KEY` en producción.
  - Manejo con un Secret Manager (Vault, AWS Secrets Manager, etc.).
- Si alguien usa este repo sin cambiar la clave, tendrá un sistema vulnerable (tokens triviales de forjar).

#### 2.3.4. CSRF, XSS y protecciones de capa HTTP

- No se ven:

  - Middleware explícitos para:
    - CSRF (aunque para API JWT-only el riesgo es menor, sigue habiendo vectores en clientes browser si se usan cookies en el futuro).
    - XSS (CSP, sanitización extra).
  - WAF o API Gateway documentado como parte del despliegue.

- PRD habla de OWASP, WAF, etc., pero a nivel conceptual.

**Conclusión:**

- A nivel API JSON con JWT en header, CSRF es menos crítico, pero:
  - No hay una **estrategia formal** incluida en el repo.
  - No hay mención explicita a “no usar cookies con SameSite lax/none” o similar.

#### 2.3.5. Auditoría y monitoreo de seguridad

- PRD menciona:

  - Logs estructurados, métricas, tracing, escaneo de vulnerabilidades.

- En el repo:

  - No se ven:
    - Middlewares de logging estructurado.
    - Configs de SAST/DAST (GitHub Actions, Sonar, etc.).
    - Rastreos de seguridad o auditoría (por ejemplo, tabla de logs de acceso o cambios críticos de estado).

---

## 3. Plan detallado de mejoras y correcciones  
*(Estilo paso a paso – instrucciones concretas y aplicables sobre este repo)*

### 3.1. Objetivo global

1. Pasar de **7/10** a al menos **8–9/10** en Seguridad y Control de Acceso.
2. Hacerlo **sin romper el MVP**, apoyándose en la arquitectura existente.
3. Dejar la base preparada para un nivel casi “bancario” cuando se añadan WAF/API Gateway y procesos de seguridad avanzados.

---

### 3.2. Paso 1 – Asegurar HTTPS en despliegue (reverse proxy + TLS)

**Objetivo:** Garantizar que en producción todo el tráfico API pase por HTTPS con TLS fuerte y HSTS.

**Pasos:**

1. **No exponer Uvicorn directamente en internet**

   - Uvicorn debe correr **detrás de un reverse proxy** (Nginx, Traefik, etc.) o un **API Gateway** (Kong, AWS API Gateway, GCP API Gateway).
   - Recomendación práctica:
     - Mantener `web` tal como está (solo HTTP interno).
     - Añadir un servicio `nginx` (o similar) que:
       - Escuche en 80/443.
       - Terminate TLS.
       - Haga proxy_pass a `web:8000`.

2. **Crear un ejemplo de configuración Nginx**

   - Añadir un archivo `nginx.conf.example` (no necesariamente en este repo, pero documentar):

     ```nginx
     server {
       listen 80;
       server_name api.conmaq.com;
       return 301 https://$host$request_uri;
     }

     server {
       listen 443 ssl http2;
       server_name api.conmaq.com;

       ssl_certificate     /etc/ssl/certs/fullchain.pem;
       ssl_certificate_key /etc/ssl/private/privkey.pem;
       ssl_protocols       TLSv1.2 TLSv1.3;
       ssl_ciphers         HIGH:!aNULL:!MD5;

       add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload" always;

       location / {
         proxy_pass http://web:8000;
         proxy_set_header Host $host;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;
       }
     }
     ```

3. **Documentar en `DOCUMENTACION_TECNICA.md`**

   - Nueva subsección en “Testing y Despliegue”: “Despliegue seguro con TLS”.
   - Explicar:
     - En dev se usa `http://localhost:8000`.
     - En prod se expone `https://api.conmaq.com` via reverse proxy.
     - FastAPI no debería escuchar internet directamente.

---

### 3.3. Paso 2 – Endurecer CORS y headers de seguridad

**Objetivo:** Reducir superficies de ataque desde navegadores y cumplir OWASP en la capa HTTP.

**Pasos:**

1. **Externalizar orígenes CORS a configuración**

   - En `app/core/config.py`, añadir:

     ```python
     from typing import List

     class Settings(BaseSettings):
         ...
         BACKEND_CORS_ORIGINS: List[str] = []
     ```

   - Permitir configurarlo via `.env` (por ejemplo, lista separada por comas).

2. **Usar `BACKEND_CORS_ORIGINS` en `main.py`**

   - Reemplazar:

     ```python
     origins = [
         "http://localhost",
         "http://localhost:3000",
         "http://localhost:8080",
     ]
     ```

   - Por algo como:

     ```python
     from app.core.config import settings

     origins = settings.BACKEND_CORS_ORIGINS or [
         "http://localhost",
         "http://localhost:3000",
         "http://localhost:8080",
     ]
     ```

   - Y en producción, definir `BACKEND_CORS_ORIGINS=["https://app.conmaq.com"]`.

3. **Restringir métodos y headers si es posible**

   - En lugar de `allow_methods=["*"]`, considerar:

     ```python
     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
     ```

   - Y `allow_headers` restringido a los realmente usados (`Authorization`, `Content-Type`, etc.), si se quiere ser estricto.

4. **Añadir middleware de headers de seguridad**

   - Crear `app/core/security_headers.py`:

     ```python
     from starlette.middleware.base import BaseHTTPMiddleware
     from starlette.responses import Response

     class SecurityHeadersMiddleware(BaseHTTPMiddleware):
         async def dispatch(self, request, call_next):
             response: Response = await call_next(request)
             response.headers["X-Content-Type-Options"] = "nosniff"
             response.headers["X-Frame-Options"] = "DENY"
             response.headers["X-XSS-Protection"] = "1; mode=block"
             # CSP se define con cuidado según frontend
             return response
     ```

   - En `main.py`:

     ```python
     from app.core.security_headers import SecurityHeadersMiddleware

     app.add_middleware(SecurityHeadersMiddleware)
     ```

---

### 3.4. Paso 3 – Gestionar secretos correctamente y habilitar rotación

**Objetivo:** Evitar secretos hardcodeados y facilit ar rotación segura.

**Pasos:**

1. **Eliminar `SECRET_KEY` por defecto “realista”**

   - En `app/core/config.py`, cambiar:

     ```python
     SECRET_KEY: str = "changethis_secret_key_for_dev"
     ```

   - Por algo como:

     ```python
     SECRET_KEY: str = "changethis_secret_key_for_dev"  # solo para dev
     ```

   Y añadir una validación sencilla:

   ```python
   import os

   class Settings(BaseSettings):
       ...
       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           if not self.DATABASE_URL:
               ...
           if os.getenv("ENV") == "production" and self.SECRET_KEY == "changethis_secret_key_for_dev":
               raise ValueError("SECRET_KEY must be set for production")
   ```

2. **Documentar variables de entorno críticas**

   - En `DOCUMENTACION_TECNICA.md` y `MANUAL_CONFIGURACION_PAGOS.md`:
     - `SECRET_KEY`
     - `STRIPE_API_KEY`
     - `STRIPE_WEBHOOK_SECRET`
   - Aclarar:
     - Deben configurarse via `.env` o Secret Manager.
     - Deben rotarse periódicamente.

3. **Recomendar Secret Manager**

   - Añadir una nota en el manual:
     - En producción, usar Vault/AWS Secrets Manager/Azure Key Vault/GCP Secret Manager.
     - No commitear `.env`.

---

### 3.5. Paso 4 – Revisar ataque CSRF y aclarar modelo de autenticación

**Objetivo:** Asegurar que el modelo actual (JWT en Authorization header) no introduzca CSRF involuntarios y dejar esto claro en la documentación.

**Pasos:**

1. **Explicitamente NO usar cookies para JWT en este diseño**

   - Documentar en `DOCUMENTACION_TECNICA.md`:
     - “El token JWT se envía únicamente en el header `Authorization: Bearer ...` y no en cookies.”
   - Esto reduce ataques CSRF clásicos basados en cookies del navegador.

2. **Si en el futuro se usan cookies, planificar CSRF**

   - Añadir un apartado “Futuro” donde se diga:
     - Si se decide usar cookies para tokens, habrá que:
       - Configurar `SameSite=strict/lax`.
       - Usar tokens anti-CSRF (double submit o similar).

3. **Sanitizar inputs en lugares sensibles (si aplica)**

   - Aunque la API es JSON y Pydantic ya valida, añadir:
     - Nota en la guía frontend: escapar contenido de usuario antes de inyectarlo en HTML.
     - (XSS se gestiona principalmente en el lado cliente en este modelo).

---

### 3.6. Paso 5 – Auditoría y logging de seguridad

**Objetivo:** Tener trazabilidad de acciones críticas (quién hizo qué y cuándo).

**Pasos:**

1. **Definir un middleware de logging de acceso básico**

   - `app/core/logging_middleware.py`:

     ```python
     import time
     import logging
     from starlette.middleware.base import BaseHTTPMiddleware
     from starlette.requests import Request

     logger = logging.getLogger("access")

     class AccessLogMiddleware(BaseHTTPMiddleware):
         async def dispatch(self, request: Request, call_next):
             start_time = time.time()
             response = await call_next(request)
             process_time = (start_time - time.time()) * -1
             client_ip = request.client.host if request.client else "unknown"
             logger.info(
                 "method=%s path=%s status=%s latency_ms=%.2f ip=%s",
                 request.method,
                 request.url.path,
                 response.status_code,
                 process_time * 1000,
                 client_ip,
             )
             return response
     ```

   - Registrar middleware en `main.py`:

     ```python
     from app.core.logging_middleware import AccessLogMiddleware
     app.add_middleware(AccessLogMiddleware)
     ```

2. **Registrar eventos de seguridad explícitos**

   - En endpoints de:
     - Login fallido.
     - Cambios de rol / permisos.
     - Creación de máquinas.
     - Operaciones de pago (`confirm_payment`).

   - Añadir logs tipo:

     ```python
     logger = logging.getLogger("security")

     logger.warning("Failed login attempt for email=%s from ip=%s", email, client_ip)
     ```

3. **Documentar cómo se recogen y analizan logs**

   - Indicar que los logs se envían a:
     - stdout → stack de logging central (ELK, Loki, etc.).
   - Recomendar:
     - Crear alertas básicas (p.ej. N intentos de login fallidos en X tiempo).

---

### 3.7. Paso 6 – Escaneo de vulnerabilidades y CI de seguridad

**Objetivo:** Convertir la seguridad en un proceso continuo, no un estado estático.

**Pasos:**

1. **Añadir una pipeline de SAST y dependencia**

   - Usar GitHub Actions (`.github/workflows/security.yml`) con:
     - `pip-audit` o `safety` para dependencias.
     - `bandit` para análisis estático Python.

2. **Ejemplo de workflow simple:**

   ```yaml
   name: Security Scan

   on:
     push:
       branches: [ main ]
     pull_request:

   jobs:
     security:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.11"
         - name: Install deps
           run: |
             cd backend
             pip install -r requirements.txt
             pip install bandit pip-audit
         - name: Bandit scan
           run: |
             cd backend
             bandit -r app -ll
         - name: Pip audit
           run: |
             cd backend
             pip-audit
   ```

3. **Planear pruebas de penetración periódicas**

   - No necesariamente codificar en repo, pero sí:
     - Documentar en `PRD_agendamiento.md` o un nuevo doc “Plan de Seguridad Operativa”.
     - Programar (aunque sea conceptualmente) pentests trimestrales/a demanda.

---

### 3.8. Paso 7 – Revisión del modelado de roles y principio de mínimo privilegio

**Objetivo:** Asegurar que los roles existentes siguen el principio de menor privilegio y que no hay endpoints sobrescopes.

**Pasos:**

1. **Enumerar roles y permisos en un documento**

   - En `DOCUMENTACION_TECNICA.md` o un `RBAC.md`:

     | Rol         | Permisos clave                                                |
     |-------------|---------------------------------------------------------------|
     | client      | Ver máquinas, crear ofertas, crear bookings propios, pagos   |
     | admin       | Ver métricas, gestionar máquinas, ver bookings globales      |
     | operator    | (si aplica) ver asignaciones, marcar check-in/out            |
     | superuser   | Todo lo anterior + gestión de usuarios                       |

2. **Mapear endpoints → roles**

   - Tabla de endpoints (ya descritos) y quién puede:

     - `/metrics/*` → `admin`/`superuser`.
     - `/machines` (POST/PUT/DELETE) → `superuser`.
     - `/offers` → `client` (autenticado).
     - `/bookings/from-offer` → dueño de la oferta.

3. **Refactorizar endpoints que usen permisos demasiado amplios**

   - Verificar que:
     - Ningún endpoint sensible utilice sólo `get_current_user` si debería usar `get_current_active_admin` o similar.
   - Ajustar si se detecta casos.

---

### 3.9. Paso 8 – Hacia el 10/10 (visión futura)

Para eventualmente llegar a una calificación **10**, el proyecto debería:

1. **Usar un API Gateway y WAF configurados**

   - Ejemplo:
     - AWS API Gateway + AWS WAF.
     - Kong + ModSecurity.
   - Reglas OWASP pre-configuradas (inyección, XSS, path traversal, etc.).

2. **Autenticación multifactor para roles sensibles**

   - MFA obligatorio para `admin` y `superuser`.
   - Integración con IdP (Auth0, Keycloak, Azure AD, etc.) para SSO + MFA.

3. **Rotación automática de claves y tokens**

   - Policies para:
     - Rotar `SECRET_KEY` en intervalos seguros.
     - Rotar claves de Stripe.
     - Invalidar JWTs antiguos tras rotación.

4. **Auditoría avanzada**

   - Logs de auditoría inmutables (append-only storage).
   - Dashboards de seguridad (picos de login fallido, cambios de permisos, etc.).
   - Alertas automáticas (SIEM).

5. **Cobertura OWASP Top 10 verificada**

   - Checklists que demuestren:
     - A1 a A10 mitigados.
   - Incluir esto en pipeline de QA.

---

## Conclusión

El backend de CONMAQ tiene una **base de seguridad muy buena** para un proyecto en Fase 3 / MVP avanzado:

- Autenticación JWT robusta con contraseñas hasheadas.
- Control de acceso por roles y dependencias.
- Rate limiting con Redis.
- Validación estricta via Pydantic.
- No se almacenan datos de pago sensibles.

Esto justifica una calificación de **7/10** en “Seguridad y Control de Acceso”.

Las principales mejoras necesarias para subir la nota se centran en:

1. Formalizar despliegue seguro: HTTPS/TLS, reverse proxy, HSTS.
2. Endurecer CORS y headers de seguridad.
3. Mejorar gestión de secretos y rotación.
4. Añadir logging/auditoría de seguridad y CI de seguridad (SAST/DAST).
5. Refinar y documentar exhaustivamente el modelo RBAC y el principio de mínimo privilegio.

Siguiendo el plan detallado anterior, se puede evolucionar gradualmente hacia una postura de seguridad cercana a la exigida por entornos de **alta criticidad** (8–9/10), y dejar el sistema listo para alcanzar un nivel casi “bancario” (10/10) cuando se integren WAF, API gateway y procesos continuos de pruebas de seguridad.