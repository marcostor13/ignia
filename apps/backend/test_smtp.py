import asyncio
import aiosmtplib
from email.mime.text import MIMEText

async def test():
    msg = MIMEText('Test desde Ignia backend')
    msg['Subject'] = 'Test SMTP Gmail'
    msg['From'] = 'admin.site@gmail.com'
    msg['To'] = 'admin.site@gmail.com'
    try:
        await aiosmtplib.send(
            msg,
            hostname='smtp.gmail.com',
            port=587,
            start_tls=True,
            username='admin.site@gmail.com',
            password='cufzrjhrstynbjdc',
        )
        print('OK — email enviado')
    except Exception as e:
        print('ERROR:', e)

asyncio.run(test())
