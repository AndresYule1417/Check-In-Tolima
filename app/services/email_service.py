import requests
from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail

class EmailService:
    @staticmethod
    def enviar_correo(destinatario, asunto, template, **kwargs):
        """
        Método profesional vía Flask-Mail (Gmail SMTP).
        Ideal para Facturas, Reservas y Seguridad.
        """
        try:
            html_body = render_template(template, **kwargs)
            msg = Message(
                subject=asunto,
                recipients=[destinatario],
                html=html_body,
                sender=current_app.config.get('MAIL_USERNAME')
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error SMTP a {destinatario}: {e}")
            return False

    @staticmethod
    def enviar_via_emailjs(template_id, template_params):
        """
        Método vía EmailJS API.
        Ideal para formularios de contacto y alertas rápidas.
        """
        service_id = "service_elis6v7"
        user_id = current_app.config.get('EMAILJS_PUBLIC_KEY')
        
        if not user_id:
            print("Error: EMAILJS_PUBLIC_KEY no configurado en .env")
            return False

        data = {
            'service_id': service_id,
            'template_id': template_id,
            'user_id': user_id,
            'template_params': template_params
        }

        try:
            response = requests.post(
                'https://api.emailjs.com/api/v1.0/email/send',
                json=data
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error EmailJS: {e}")
            return False

def enviar_correo_bienvenida(usuario, mail_ext):
    """Mantenido por compatibilidad con el flujo de registro."""
    try:
        asunto = "¡Bienvenido a Check-In Viajes Tolima! 🌿"
        html_body = render_template('emails/bienvenida.html', usuario=usuario)
        msg = Message(
            subject=asunto,
            recipients=[usuario.correo],
            html=html_body,
            sender=current_app.config.get('MAIL_USERNAME')
        )
        mail_ext.send(msg)
        return True
    except Exception as e:
        print(f"Error Bienvenida SMTP: {e}")
        return False
