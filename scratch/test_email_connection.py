import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def test_smtp():
    server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    port = int(os.getenv('MAIL_PORT', 587))
    user = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    
    print(f"Intentando conectar a {server}:{port} con {user}...")
    
    try:
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(user, password)
        print("✅ ¡ÉXITO! La conexión con Gmail es correcta.")
        smtp.quit()
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        if "Username and Password not accepted" in str(e):
            print("\nNOTA: Google rechazó tu contraseña. Esto confirma que necesitas usar una 'Contraseña de Aplicación' de 16 letras, no tu clave normal.")

if __name__ == "__main__":
    test_smtp()
