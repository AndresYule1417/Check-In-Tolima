from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.reserva import Reserva
import os
from werkzeug.utils import secure_filename

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/mi-perfil')
@login_required
def mi_perfil():
    """Vista principal del perfil del usuario con sus reservas."""
    reservas = Reserva.query.filter_by(usuario_id=current_user.id).order_by(Reserva.fecha_reserva.desc()).all()
    return render_template('perfil/mi-perfil.html', reservas=reservas, active_tab='reservas')

@perfil_bp.route('/mi-perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Permite al usuario editar su información personal y foto."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        nueva_pass = request.form.get('password')
        
        # Manejo de avatar (idéntico al admin)
        foto = request.files.get('avatar')
        if foto and foto.filename != '':
            filename = secure_filename(f"user_{current_user.id}_{foto.filename}")
            upload_path = os.path.join(current_app.root_path, 'static/uploads/avatars')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            foto.save(os.path.join(upload_path, filename))
            current_user.avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')

        if not nombre or not correo:
            flash("Nombre y correo son obligatorios.", "error")
        else:
            current_user.nombre = nombre
            current_user.correo = correo
            if nueva_pass:
                current_user.set_password(nueva_pass)
            
            db.session.commit()
            flash("Tu perfil ha sido actualizado correctamente.", "success")
            return redirect(url_for('perfil.mi_perfil'))

    return render_template('perfil/editar.html', usuario=current_user, active_tab='editar')

@perfil_bp.route('/mi-perfil/reserva/<codigo>')
@login_required
def detalle_reserva(codigo):
    """Muestra el detalle extendido de una reserva específica."""
    reserva = Reserva.query.filter_by(codigo_ref=codigo, usuario_id=current_user.id).first_or_404()
    return render_template('perfil/detalle_reserva.html', reserva=reserva, active_tab='reservas')
