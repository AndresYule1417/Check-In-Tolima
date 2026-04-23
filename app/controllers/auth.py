from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.usuario import Usuario
from app.extensions import db, mail
from app.services.email_service import enviar_correo_bienvenida, EmailService
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        rol = request.form.get('rol', 'usuario')
        if rol == 'user': rol = 'usuario'

        if not nombre or not correo or not password or not password_confirm:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('auth.registro'))

        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('auth.registro'))
            
        usuario_existente = Usuario.query.filter_by(correo=correo).first()
        if usuario_existente:
            flash('El correo electrónico ya está registrado.', 'warning')
            return redirect(url_for('auth.registro'))

        try:
            nuevo_usuario = Usuario(nombre=nombre, correo=correo, rol=rol, verificado=False, activo=True)
            nuevo_usuario.set_password(password)
            db.session.add(nuevo_usuario)
            db.session.commit()

            # Enviar correo de verificación vía EmailJS
            token = nuevo_usuario.get_token(salt='email-confirm')
            link_verificacion = url_for('auth.verificar_email', token=token, _external=True)
            
            EmailService.enviar_via_emailjs(
                template_id='template_792xa2d',
                template_params={
                    'name': nuevo_usuario.nombre,
                    'link': link_verificacion,
                    'time': datetime.now().strftime('%d/%m/%Y %H:%M')
                }
            )

            flash('¡Registro exitoso! Por favor verifica tu correo electrónico para activar tu cuenta.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la cuenta.', 'error')
            return redirect(url_for('auth.registro'))

    return render_template('auth/registro.html')

@auth_bp.route('/verificar-email/<token>')
def verificar_email(token):
    usuario = Usuario.verify_token(token, salt='email-confirm')
    if not usuario:
        flash('El enlace de verificación es inválido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))
    
    usuario.verificado = True
    db.session.commit()
    flash('¡Cuenta verificada con éxito! Ya puedes iniciar sesión.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('viajes.catalogo'))

    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and usuario.check_password(password):
            if not usuario.activo:
                flash('Esta cuenta ha sido desactivada.', 'error')
                return redirect(url_for('auth.login'))
            
            # Login directo (Verificación opcional por ahora)
            login_user(usuario)
            flash('¡Bienvenido de nuevo!', 'success')
            return redirect(url_for('viajes.catalogo'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/olvide-password', methods=['GET', 'POST'])
def olvide_password():
    if request.method == 'POST':
        correo = request.form.get('correo')
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario:
            token = usuario.get_token(salt='password-reset')
            link_reset = url_for('auth.restablecer_password', token=token, _external=True)
            EmailService.enviar_correo(
                destinatario=usuario.correo,
                asunto="Restablecer Contraseña - Check-In Tolima",
                template='emails/restablecer_pass.html',
                usuario=usuario,
                link=link_reset
            )
        flash('Si el correo existe, hemos enviado un enlace para restablecer tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/olvide_password.html')

@auth_bp.route('/restablecer-password/<token>', methods=['GET', 'POST'])
def restablecer_password(token):
    usuario = Usuario.verify_token(token, salt='password-reset')
    if not usuario:
        flash('El enlace es inválido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('password_confirm')
        if password == confirm:
            usuario.set_password(password)
            db.session.commit()
            flash('Contraseña actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        flash('Las contraseñas no coinciden.', 'error')
    
    return render_template('auth/restablecer_password.html', token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('publico.inicio'))
