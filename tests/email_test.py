import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

def send_test_email():
    msg = MIMEText("Questo è un test del Language Mentor!")
    msg['Subject'] = 'Test Configurazione Email'
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = os.getenv("EMAIL_FROM")  # Invia a te stesso

    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.ehlo()
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            server.sendmail(os.getenv("EMAIL_FROM"), [os.getenv("EMAIL_FROM")], msg.as_string())
        print("✅ Email inviata con successo! Controlla la tua inbox (e spam)")
    except Exception as e:
        print(f"❌ Errore: {str(e)}")

if __name__ == "__main__":
    send_test_email()