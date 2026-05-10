# Ignia — Guía completa de configuración y despliegue

Última actualización: Mayo 2026

---

## Índice

1. [Arquitectura general](#1-arquitectura-general)
2. [Variables de entorno](#2-variables-de-entorno)
3. [Configuración de WhatsApp Cloud API](#3-configuración-de-whatsapp-cloud-api)
4. [Configuración de APIs de IA](#4-configuración-de-apis-de-ia)
5. [Desarrollo local](#5-desarrollo-local)
6. [Despliegue en Netlify](#6-despliegue-en-netlify)
7. [Flujo de leads (formulario → WhatsApp)](#7-flujo-de-leads-formulario--whatsapp)
8. [Agentes de IA disponibles](#8-agentes-de-ia-disponibles)
9. [API Reference](#9-api-reference)
10. [Gestión de leads (base de datos)](#10-gestión-de-leads-base-de-datos)
11. [Activar IA real (Claude / Gemini)](#11-activar-ia-real-claude--gemini)
12. [Solución de problemas](#12-solución-de-problemas)

---

## 1. Arquitectura general

```
ignia/
├── apps/
│   ├── frontend/          # Angular 21 — SPA estática
│   └── backend/           # Python 3.13 — FastAPI
│       ├── api/           # Rutas HTTP
│       │   ├── main.py    # App principal + 6 endpoints
│       │   └── leads.py   # Lead capture + webhook WhatsApp
│       ├── agents/        # Agentes de IA
│       │   ├── demo_agent.py    # Respuestas por palabras clave (sin API key)
│       │   ├── claude_agent.py  # Anthropic Claude
│       │   ├── gemini_agent.py  # Google Gemini
│       │   └── registry.py     # 5 agentes registrados
│       ├── whatsapp/
│       │   └── client.py  # WhatsApp Cloud API v20.0
│       ├── models/
│       │   └── lead.py    # SQLite: tabla leads
│       ├── skills/        # Habilidades reutilizables (search_web, write_code, summarize…)
│       └── token_efficiency/  # Compressor, Tracker, PromptCache
├── netlify/functions/
│   └── api.py             # Wrapper Mangum: FastAPI → Netlify Function
├── data/
│   └── leads.db           # SQLite (creado automáticamente)
├── netlify.toml           # Configuración de build y redirects
└── .env                   # Variables de entorno (NO subir a git)
```

**Flujo de petición en producción:**

```
Browser → Netlify CDN (Angular static)
         → /api/* → Netlify Function (Python/FastAPI via Mangum)
```

---

## 2. Variables de entorno

Copia `.env.example` a `.env` y rellena los valores:

```bash
cp .env.example .env
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `WHATSAPP_PHONE_NUMBER_ID` | Sí* | ID del número de teléfono en Meta |
| `WHATSAPP_ACCESS_TOKEN` | Sí* | Token permanente de sistema (Meta Business) |
| `WHATSAPP_NOTIFY_PHONE` | Sí* | Teléfono del equipo Ignia (con código de país, sin +) |
| `WHATSAPP_COMMUNITY_URL` | Sí* | Link de invitación al grupo de WhatsApp |
| `WHATSAPP_VERIFY_TOKEN` | Sí | Token para verificar webhook (default: `ignia_verify_2024`) |
| `WHATSAPP_WELCOME_TEMPLATE` | No | Nombre del template de bienvenida (default: `ignia_bienvenida_taller`) |
| `ANTHROPIC_API_KEY` | No† | API key de Anthropic Claude |
| `GOOGLE_API_KEY` | No† | API key de Google Gemini |
| `CLAUDE_MODEL` | No | Modelo Claude (default: `claude-sonnet-4-6`) |
| `GEMINI_MODEL` | No | Modelo Gemini (default: `gemini-2.0-flash`) |
| `APP_ENV` | No | `development` o `production` |
| `ALLOWED_ORIGINS` | No | CORS origins permitidos |

*Sin estas variables el chat funciona (DemoAgent no usa API), pero no se enviarán notificaciones WhatsApp.
†Sin estas variables el chat usa DemoAgent (respuestas por palabras clave en español).

---

## 3. Configuración de WhatsApp Cloud API

### 3.1 Crear una app en Meta for Developers

1. Ve a [developers.facebook.com](https://developers.facebook.com) → **My Apps** → **Create App**
2. Tipo: **Business**
3. Agrega el producto **WhatsApp**

### 3.2 Obtener el Phone Number ID y Access Token

1. En tu app → **WhatsApp** → **API Setup**
2. En **Step 1**: copia el **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID`
3. Para un token permanente:
   - Ve a **Business Settings** → **System Users** → crea un usuario de sistema
   - Asígnale el rol **Admin** en tu cuenta de WhatsApp Business
   - Genera un token con permiso `whatsapp_business_messaging`
   - Copia el token → `WHATSAPP_ACCESS_TOKEN`

> **Importante:** El token temporal de la API Setup expira en 24h. Siempre usa un System User Token permanente.

### 3.3 Configurar el webhook en Meta

El webhook permite recibir mensajes entrantes y verificar la integración.

**URL del webhook en producción:**
```
https://TU_SITIO.netlify.app/.netlify/functions/api/api/leads/webhook
```

**Pasos:**
1. En tu app Meta → **WhatsApp** → **Configuration** → **Webhook**
2. **Callback URL**: la URL anterior
3. **Verify Token**: el mismo valor que `WHATSAPP_VERIFY_TOKEN` en tu `.env` (default: `ignia_verify_2024`)
4. Suscríbete al evento: **messages**
5. Haz clic en **Verify and Save** → Meta hará una petición GET al webhook con `hub.challenge`

### 3.4 Configurar el número de teléfono de notificaciones

En `WHATSAPP_NOTIFY_PHONE` pon el número del equipo Ignia en formato internacional sin `+`:

```
# Argentina +54 11 1234-5678
WHATSAPP_NOTIFY_PHONE=541112345678

# México +52 55 1234-5678
WHATSAPP_NOTIFY_PHONE=525512345678
```

### 3.5 Crear el grupo de comunidad y obtener el link

1. En WhatsApp → crea un grupo → **Enlace de invitación** → copia el link
2. Pega el link en `WHATSAPP_COMMUNITY_URL`:
```
WHATSAPP_COMMUNITY_URL=https://chat.whatsapp.com/XXXXXXXXXXXXXXXXXXXXXX
```

### 3.6 Template de bienvenida (opcional)

Si quieres enviar un mensaje de bienvenida automático a leads que dejen su teléfono:

1. En Meta Business Manager → **WhatsApp** → **Message Templates** → **Create Template**
2. Categoría: **Marketing**
3. Nombre: `ignia_bienvenida_taller` (o el que configures en `WHATSAPP_WELCOME_TEMPLATE`)
4. Idioma: **Español**
5. Cuerpo del template (ejemplo):
   ```
   ¡Hola {{1}}! 👋

   Gracias por inscribirte al Taller Gratuito de Ignia.
   Te compartiremos todos los detalles pronto.

   ¡Nos vemos! 🚀
   ```
   El parámetro `{{1}}` se reemplaza con el primer nombre del lead.
6. Espera aprobación de Meta (normalmente < 24h)

> Si el template no está aprobado o no existe, el backend simplemente omite el mensaje de bienvenida al lead; la notificación al equipo sigue funcionando.

---

## 4. Configuración de APIs de IA

### Anthropic Claude

1. Crea cuenta en [console.anthropic.com](https://console.anthropic.com)
2. **API Keys** → **Create Key**
3. Copia la clave → `ANTHROPIC_API_KEY=sk-ant-...`
4. Los agentes `coding_agent` y `analysis_agent` usan Claude

### Google Gemini

1. Ve a [aistudio.google.com](https://aistudio.google.com) → **Get API Key**
2. Copia la clave → `GOOGLE_API_KEY=AIza...`
3. Los agentes `chat_agent` y `document_agent` usan Gemini

> **Sin API keys:** El sitio funciona completo. El chat usa `website_agent` (DemoAgent) que responde con palabras clave en español sobre los servicios de Ignia, sin coste ni dependencias externas.

---

## 5. Desarrollo local

### Requisitos

- Node.js 20+ y npm
- Python 3.11+
- `pip install uv` (recomendado) o pip directo

### Setup inicial

```bash
# Frontend
cd apps/frontend
npm install

# Backend
cd apps/backend
pip install -r requirements.txt
# o con uv:
uv pip install -r requirements.txt
```

### Iniciar el frontend (Angular)

```bash
cd apps/frontend
npm start
# → http://localhost:4200
```

### Iniciar el backend (FastAPI)

```bash
# Desde la raíz del proyecto
uvicorn apps.backend.api.main:app --reload --port 8000

# O desde apps/backend:
cd apps/backend
uvicorn api.main:app --reload --port 8000
# → http://localhost:8000
```

### Usar Netlify CLI (recomendado para simular producción)

```bash
npm install -g netlify-cli

# Desde la raíz
netlify dev
# Frontend en http://localhost:8888
# Backend en http://localhost:8888/api/*
```

Con `netlify dev` los redirects de `netlify.toml` funcionan igual que en producción: `/api/*` se proxea automáticamente a la función Python.

---

## 6. Despliegue en Netlify

### 6.1 Conectar el repositorio

1. [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import an existing project**
2. Conecta tu repositorio de GitHub/GitLab
3. Netlify detecta `netlify.toml` automáticamente

### 6.2 Configurar variables de entorno en Netlify

1. **Site settings** → **Environment variables** → **Add variable**
2. Agrega todas las variables del apartado [2. Variables de entorno](#2-variables-de-entorno)

> Las variables de entorno en Netlify se aplican a **funciones** y al **build**. El frontend Angular las lee en tiempo de build solo si usas `environment.ts` (actualmente las variables de API se leen en el backend, no en Angular).

### 6.3 Build settings (ya configurados en netlify.toml)

| Setting | Valor |
|---|---|
| Build command | `cd apps/frontend && npm ci && npm run build` |
| Publish directory | `apps/frontend/dist/frontend/browser` |
| Functions directory | `netlify/functions` |
| Node version | 24 |
| Python version | 3.13 |

### 6.4 Primer deploy

```bash
# Deploy manual desde CLI
netlify deploy --prod

# O simplemente haz push a main → deploy automático
git push origin main
```

### 6.5 Configurar el webhook de WhatsApp tras el deploy

Una vez que el sitio esté en línea con una URL fija, actualiza el webhook en Meta:

```
Callback URL: https://TU-SITIO.netlify.app/.netlify/functions/api/api/leads/webhook
```

---

## 7. Flujo de leads (formulario → WhatsApp)

```
Usuario completa el formulario (email + nombre opcional)
    ↓
POST /api/leads
    ↓
SQLite: INSERT o recupera registro existente (upsert por email)
    ↓ (si es lead nuevo)
BackgroundTask: whatsapp.notify_new_lead()
    → Envía mensaje de texto al equipo (WHATSAPP_NOTIFY_PHONE)
    ↓ (si el lead dio su teléfono)
BackgroundTask: whatsapp.send_welcome_to_lead()
    → Envía template de bienvenida al lead
    ↓
Respuesta HTTP 201:
    {
      "success": true,
      "already_registered": false,
      "message": "¡Tu lugar está reservado! ...",
      "whatsapp_community_url": "https://chat.whatsapp.com/..."
    }
    ↓
Frontend muestra botón "Unirse a la comunidad de WhatsApp"
```

**Mensaje que recibe el equipo Ignia:**
```
🔔 *Nuevo lead — Taller Gratuito*

📧 Email: usuario@ejemplo.com
👤 Nombre: María García
📌 Fuente: Taller Gratuito
🕐 09/05/2026 14:32 UTC

¡Responde cuanto antes para cerrar la oportunidad! 🚀
```

---

## 8. Agentes de IA disponibles

| ID | Nombre | Modelo | Uso |
|---|---|---|---|
| `website_agent` | Asistente Ignia | DemoAgent (sin API) | Chat del sitio web — consultas sobre servicios |
| `coding_agent` | Coding Agent | Claude | Generación y revisión de código |
| `analysis_agent` | Analysis Agent | Claude | Análisis de datos y documentos |
| `chat_agent` | Chat Agent | Gemini | Conversación general |
| `document_agent` | Document Agent | Gemini | Procesamiento de documentos |

### DemoAgent (website_agent)

Responde en español usando detección de palabras clave por categorías:

- **servicios** → qué hace Ignia
- **web / app** → desarrollo web y móvil
- **precio / presupuesto** → invita a agendar llamada
- **tiempo / plazo** → tiempos de entrega típicos
- **tecnologia / stack** → tecnologías que usan
- **ia / inteligencia artificial** → servicios de IA
- **ecommerce / tienda** → e-commerce
- **proceso** → cómo trabaja Ignia
- **contacto / llamada** → cómo contactar
- **soporte / mantenimiento** → soporte post-entrega
- **taller / curso** → taller gratuito
- **saludo** → bienvenida
- **gracias** → despedida
- **default** → invitación a describir el proyecto

---

## 9. API Reference

### `POST /api/leads`

Registra un lead para el taller gratuito.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "name": "María García",
  "phone": "541112345678",
  "source": "taller"
}
```
`name`, `phone` y `source` son opcionales. `source` tiene default `"taller"`.

**Response 201:**
```json
{
  "success": true,
  "already_registered": false,
  "message": "¡Tu lugar está reservado! Te esperamos en la comunidad.",
  "whatsapp_community_url": "https://chat.whatsapp.com/..."
}
```

---

### `GET /api/leads`

Lista todos los leads capturados (endpoint de administración).

```
GET /api/leads?limit=100
```

**Response:**
```json
{
  "total": 42,
  "leads": [
    {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "name": "María",
      "phone": null,
      "source": "taller",
      "whatsapp_notified": true,
      "created_at": "2026-05-09T14:32:00Z"
    }
  ]
}
```

---

### `GET /api/leads/webhook`

Verificación del webhook de Meta (llamado por Meta al configurarlo).

```
GET /api/leads/webhook?hub.mode=subscribe&hub.verify_token=ignia_verify_2024&hub.challenge=12345
```

Devuelve el valor de `hub.challenge` si el token coincide.

---

### `POST /api/leads/webhook`

Recibe mensajes entrantes de WhatsApp (payload de Meta).

---

### `POST /api/chat`

Chat con un agente de IA.

**Request:**
```json
{
  "message": "¿Cuánto cuesta hacer una página web?",
  "agent_id": "website_agent",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "El precio varía según la complejidad del proyecto...",
  "agent_id": "website_agent",
  "tokens_used": {"input": 0, "output": 0},
  "tokens_saved": 0,
  "cost_usd": 0.0
}
```

---

### `GET /api/agents`

Lista todos los agentes disponibles.

### `GET /api/skills`

Lista todas las habilidades registradas con sus esquemas de parámetros.

### `GET /api/token-stats`

Estadísticas de uso de tokens y ahorro por caché.

### `POST /api/compress`

Comprime un prompt para reducir tokens.

**Request:**
```json
{
  "text": "texto largo a comprimir",
  "ratio": 0.7
}
```

### `GET /health`

Health check del backend.

---

## 10. Gestión de leads (base de datos)

Los leads se guardan en `data/leads.db` (SQLite, creado automáticamente).

**En desarrollo local**, el archivo está en la raíz del proyecto.

**En Netlify**, el sistema de archivos es efímero (cada deploy crea una nueva instancia). Para producción real considera:
- Usar **Netlify KV** o **Supabase** (PostgreSQL) como alternativa a SQLite
- O exportar los leads periódicamente via `GET /api/leads` y guardarlos externamente

**Ver leads desde la línea de comandos:**
```bash
sqlite3 data/leads.db "SELECT * FROM leads ORDER BY created_at DESC;"
```

**Ver leads via API (en producción):**
```
GET https://TU-SITIO.netlify.app/api/leads
```

> Recomendación: proteger este endpoint con un token de autenticación antes de lanzar a producción.

---

## 11. Activar IA real (Claude / Gemini)

Actualmente el chat del sitio usa `website_agent` (DemoAgent, sin API key). Para activar IA real:

### Opción A: Cambiar website_agent a Claude

En `apps/backend/agents/registry.py`, cambia la configuración de `website_agent`:

```python
AgentConfig(
    id="website_agent",
    model="claude",          # antes: "demo"
    ...
)
```

Asegúrate de tener `ANTHROPIC_API_KEY` configurado.

### Opción B: Usar un agente existente

El frontend puede enviar `agent_id` diferente al hacer la petición. Para cambiar el agente por defecto del chat del sitio, edita `home.component.ts`:

```typescript
// Busca la llamada al servicio de chat y cambia:
agent_id: 'website_agent'  // → 'chat_agent' (Gemini) o 'coding_agent' (Claude)
```

### Token efficiency con Claude

Cuando uses Claude, el sistema incluye automáticamente:
- **Prompt caching** (`cache_control: ephemeral`): ahorra ~90% en tokens repetidos del system prompt
- **PromptCompressor**: reduce tokens de entrada ~53% eliminando muletillas y extrayendo frases clave
- **TokenTracker**: registra uso y ahorro en `/api/token-stats`

---

## 12. Solución de problemas

### El chat no responde / timeout

- Verifica que el backend esté corriendo (`GET /health`)
- En local: comprueba que uvicorn esté en el puerto correcto
- En Netlify: revisa los logs de la función en **Functions** → **api** → **Logs**

### WhatsApp no envía notificaciones

1. Verifica que `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN` y `WHATSAPP_NOTIFY_PHONE` estén configurados
2. El token de acceso debe ser un **System User Token** permanente (no el temporal de API Setup)
3. El número receptor debe haber enviado al menos un mensaje al número de WhatsApp Business en los últimos 24h (para mensajes de texto libre)
4. Revisa los logs: `logger.warning("WhatsApp notify skipped/failed...")`

### Error 401 de WhatsApp API

El Access Token expiró o no tiene permisos. Genera un nuevo System User Token con permiso `whatsapp_business_messaging`.

### El webhook de Meta falla la verificación

- Asegúrate de que `WHATSAPP_VERIFY_TOKEN` en tu `.env` y en Meta son **exactamente iguales** (case-sensitive)
- La URL del webhook debe ser HTTPS y accesible públicamente (no funciona en localhost)
- Usa `netlify dev` + ngrok para probar webhooks en local:
  ```bash
  ngrok http 8888
  # Webhook URL: https://xxxx.ngrok.io/.netlify/functions/api/api/leads/webhook
  ```

### Error en build de Angular (budget exceeded)

El presupuesto de CSS está configurado en `angular.json`:
- Warning: 24kB
- Error: 48kB

Si el SCSS supera estos límites, aumenta los valores en `angular.json` → `projects.frontend.architect.build.configurations.production.budgets`.

### leads.db no persiste en Netlify

SQLite en Netlify Functions es volátil (el sistema de archivos se resetea en cada deploy). Para persistencia real en producción:
1. Usa **Supabase** (PostgreSQL gratuito) y reemplaza `models/lead.py` con el cliente de Supabase
2. O usa **Netlify Blobs** para almacenamiento key-value
3. Como mínimo, exporta leads regularmente con `GET /api/leads` y guárdalos en una hoja de cálculo

---

## Checklist de go-live

- [ ] `.env` completo con todas las variables de WhatsApp
- [ ] System User Token permanente de Meta configurado
- [ ] Grupo de comunidad de WhatsApp creado y link copiado en `WHATSAPP_COMMUNITY_URL`
- [ ] Template `ignia_bienvenida_taller` aprobado en Meta (si quieres welcome automático)
- [ ] Variables de entorno configuradas en Netlify (no en `.env`)
- [ ] Webhook de Meta configurado con la URL de producción
- [ ] Verificación del webhook exitosa (botón "Verify and Save" en Meta)
- [ ] Test end-to-end: completar el formulario del taller y verificar que llega notificación en WhatsApp
- [ ] `GET /api/leads` devuelve el lead capturado en el test
- [ ] Endpoint `/api/leads` protegido con autenticación (recomendado antes de lanzar)
