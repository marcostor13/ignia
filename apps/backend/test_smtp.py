import asyncio
import aiosmtplib
from email.mime.text import MIMEText

async def test():
    msg = MIMEText('Test desde Ignia backend')
    msg['Subject'] = 'Test SMTP'
    msg['From'] = 'admin@ignia.site'
    msg['To'] = 'admin@ignia.site'
    try:
        await aiosmtplib.send(
            msg,
            hostname='smtp.office365.com',
            port=587,
            start_tls=True,
            username='admin@ignia.site',
            password='@Libido2010',
        )
        print('OK — email enviado')
    except Exception as e:
        print('ERROR:', e)

asyncio.run(test())
