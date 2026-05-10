# Configuración de correo — Outlook / Microsoft 365

La plataforma usa `admin@ignia.site` para dos cosas:
- Enviar el **email de confirmación** al lead cuando se registra
- Enviar la **notificación interna** al equipo cuando llega un nuevo lead

Servidor SMTP: `smtp.office365.com:587` (STARTTLS)

---

## Opción A — Contraseña directa (MFA desactivado)

Si la cuenta `admin@ignia.site` **no tiene autenticación de dos factores (MFA)** activa:

1. Agrega en `.env`:
   ```
   EMAIL_FROM=admin@ignia.site
   EMAIL_PASSWORD=TU_CONTRASEÑA_DE_LA_CUENTA
   ```
2. Listo. No se necesita nada más.

> **Recomendación:** Usa esta opción solo en desarrollo o si la cuenta es exclusivamente para envío de emails y no tiene datos sensibles.

---

## Opción B — App Password (MFA activado, recomendado)

Si la cuenta tiene MFA habilitado (o si querés una credencial revocable sin exponer la contraseña real):

### Pasos para generar un App Password

1. Inicia sesión en [account.microsoft.com](https://account.microsoft.com) con `admin@ignia.site`
2. Ve a **Seguridad** → **Opciones de seguridad avanzadas**
3. En la sección **Contraseñas de aplicación** → **Crear una nueva contraseña de aplicación**
4. Ponle un nombre descriptivo, por ejemplo: `ignia-backend-smtp`
5. Copia la contraseña generada (solo se muestra una vez)
6. Agrega en `.env`:
   ```
   EMAIL_FROM=admin@ignia.site
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   ← la app password (con o sin espacios)
   ```

> Las App Passwords solo están disponibles si la cuenta tiene MFA habilitado.
> Si MFA no está activo, usa la Opción A o actívalo primero.

---

## Opción C — Microsoft 365 admin (dominio corporativo)

Si `admin@ignia.site` está en un tenant de Microsoft 365 administrado:

### Verificar que SMTP AUTH esté habilitado

1. Entra al **Microsoft 365 Admin Center**: [admin.microsoft.com](https://admin.microsoft.com)
2. Ve a **Users** → **Active users** → selecciona `admin@ignia.site`
3. Tab **Mail** → **Manage email apps**
4. Asegúrate de que **Authenticated SMTP** esté habilitado (checkbox marcado)
5. Guarda los cambios

### Generar App Password (si MFA está activo)

Mismos pasos que la Opción B, pero iniciando sesión con las credenciales de Microsoft 365.

---

## Configuración en Netlify

En producción, las variables van en **Netlify → Site settings → Environment variables**:

| Variable | Valor |
|---|---|
| `EMAIL_FROM` | `admin@ignia.site` |
| `EMAIL_PASSWORD` | Tu contraseña o App Password |

---

## Verificar que funciona

Después de configurar, reinicia el backend y registra un lead de prueba en `/taller`. Deberías recibir:

1. Un email en `admin@ignia.site` con el asunto `🔔 Nuevo lead: ...`
2. Un email de confirmación en el correo del lead con el asunto `✅ Tu cupo está reservado...`

Si el email no llega, revisa los logs del backend:
```
Email failed → ... | ...
```

### Causas comunes de error

| Error | Causa | Solución |
|---|---|---|
| `535 Authentication unsuccessful` | Contraseña incorrecta o SMTP AUTH desactivado | Verifica la contraseña o activa SMTP AUTH en el admin center |
| `535 5.7.139 Authentication unsuccessful` | MFA activo sin App Password | Crea un App Password (Opción B) |
| `Connection timeout` | Firewall bloqueando el puerto 587 | Verifica la configuración de red o usa un proxy |
| `Email not configured` | `EMAIL_PASSWORD` está vacío | Agrega la variable al `.env` o a Netlify |
