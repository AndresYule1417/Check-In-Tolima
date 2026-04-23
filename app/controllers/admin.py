from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.models.usuario import Usuario
from app.models.viaje import Viaje
from app.models.reserva import Reserva
from app.extensions import db
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Aplicar decoradores a todo el Blueprint
@admin_bp.before_request
@login_required
@admin_required
def before_request():
    pass

@admin_bp.route('/')
def dashboard():
    """
    Dashboard principal del administrador con métricas globales y datos para gráficas.
    """
    # Cálculos para métricas rápidas
    total_usuarios = Usuario.query.count()
    viajes_activos = Viaje.query.filter_by(activo=True).count()
    reservas_pendientes = Reserva.query.filter_by(estado='pendiente').count()
    ingresos_aprox = sum([r.total for r in Reserva.query.filter_by(estado='confirmada').all()])

    # Datos para Gráfica de Categorías (Viajes por Categoría)
    stats_categorias = db.session.query(
        Viaje.categoria, func.count(Viaje.id)
    ).filter(Viaje.activo == True).group_by(Viaje.categoria).all()
    
    cat_labels = [c[0].capitalize() for c in stats_categorias]
    cat_values = [c[1] for c in stats_categorias]

    # Datos para Tendencia de Reservas (Últimos 7 días) - Mockeado para la demo si no hay datos suficientes
    # En producción se usaría: db.session.query(func.date(Reserva.fecha_reserva), func.count(Reserva.id))...
    dias_semana = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
    ventas_mock = [12, 19, 3, 5, 2, 3, 10] # Simulando fluctuación de reservas

    # Últimas 5 reservas
    ultimas_reservas = Reserva.query.order_by(Reserva.fecha_reserva.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_usuarios=total_usuarios,
        viajes_activos=viajes_activos,
        reservas_pendientes=reservas_pendientes,
        ingresos_aprox=ingresos_aprox,
        ultimas_reservas=ultimas_reservas,
        cat_labels=cat_labels,
        cat_values=cat_values,
        dias_semana=dias_semana,
        ventas_mock=ventas_mock
    )

@admin_bp.route('/usuarios')
def usuarios():
    """Listado de usuarios con métricas de gestión."""
    from datetime import date
    todos_usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    
    # Métricas para tarjetas
    total_usuarios = len(todos_usuarios)
    total_admins = Usuario.query.filter_by(rol='admin').count()
    registrados_hoy = len([u for u in todos_usuarios if u.fecha_registro.date() == date.today()])
    return render_template(
        'admin/usuarios.html', 
        usuarios=todos_usuarios,
        total_usuarios=total_usuarios,
        total_admins=total_admins,
        registrados_hoy=registrados_hoy
    )

@admin_bp.route('/perfil', methods=['GET', 'POST'])
def mi_perfil():
    """Permite al administrador editar sus datos personales y subir foto de perfil."""
    import os
    from werkzeug.utils import secure_filename
    from app.extensions import db
    from flask import request, flash, redirect, url_for, current_app
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        nueva_pass = request.form.get('password')
        
        # Manejo de archivo de imagen
        foto = request.files.get('avatar')
        if foto and foto.filename != '':
            filename = secure_filename(f"admin_{current_user.id}_{foto.filename}")
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
            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for('admin.mi_perfil'))
            
    return render_template('admin/perfil.html', usuario=current_user)

@admin_bp.route('/usuarios/rol/<int:id>', methods=['POST'])
def cambiar_rol_usuario(id):
    """Convierte a un usuario normal en administrador o viceversa."""
    from app.extensions import db
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        flash("No puedes cambiar tu propio rol.", "warning")
    else:
        # Corregido: 'usuario' en lugar de 'user'
        usuario.rol = 'admin' if usuario.rol == 'usuario' else 'usuario'
        db.session.commit()
        flash(f"Rol de {usuario.nombre} actualizado a {usuario.rol}.", "success")
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/estado/<int:id>', methods=['POST'])
def cambiar_estado_usuario(id):
    """Activa o desactiva a un usuario."""
    from app.extensions import db
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        flash("No puedes desactivarte a ti mismo.", "warning")
    else:
        usuario.activo = not usuario.activo
        db.session.commit()
        estado_str = "activado" if usuario.activo else "desactivado"
        flash(f"Usuario {usuario.nombre} ha sido {estado_str}.", "info")
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/viajes')
def viajes():
    """Listado de viajes con analítica de inventario."""
    from app.extensions import db
    from app.models.reserva import Reserva
    from sqlalchemy import func

    # Todos los viajes (incluyendo inactivos para gestión)
    todos_viajes = Viaje.query.order_by(Viaje.id.desc()).all()
    
    # Métricas para tarjetas
    total_destinos = len(todos_viajes)
    alertas_cupo = Viaje.query.filter(Viaje.cupos_disp < 5, Viaje.activo == True).count()
    
    # Encontrar el viaje más vendido (con más reservas confirmadas)
    mejor_viaje_data = db.session.query(
        Reserva.viaje_id, func.count(Reserva.id)
    ).filter(Reserva.estado == 'confirmada').group_by(Reserva.viaje_id).order_by(func.count(Reserva.id).desc()).first()
    
    mejor_viaje = "Ninguno aún"
    if mejor_viaje_data:
        v = Viaje.query.get(mejor_viaje_data[0])
        if v: mejor_viaje = v.nombre

    return render_template(
        'admin/viajes.html', 
        viajes=todos_viajes,
        total_destinos=total_destinos,
        alertas_cupo=alertas_cupo,
        mejor_viaje=mejor_viaje
    )

@admin_bp.route('/viajes/nuevo', methods=['GET', 'POST'])
def nuevo_viaje():
    """Formulario y lógica para crear un nuevo viaje."""
    from app.extensions import db
    from datetime import datetime

    if request.method == 'POST':
        try:
            nuevo = Viaje(
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion'),
                precio=float(request.form.get('precio')),
                fecha_inicio=datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date(),
                duracion_min=int(request.form.get('duracion_min')),
                imagen_url=request.form.get('imagen_url'),
                cupos_total=int(request.form.get('cupos_total')),
                cupos_disp=int(request.form.get('cupos_total')),
                categoria=request.form.get('categoria'),
                descuento_pct=int(request.form.get('descuento_pct') or 0),
                activo=True
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Viaje creado exitosamente.', 'success')
            return redirect(url_for('admin.viajes'))
        except Exception as e:
            flash(f'Error al crear el viaje: {e}', 'error')

    return render_template('admin/viaje_form.html', viaje=None)

@admin_bp.route('/viajes/editar/<int:id>', methods=['GET', 'POST'])
def editar_viaje(id):
    """Formulario y lógica para editar un viaje existente."""
    from app.extensions import db
    from datetime import datetime

    viaje = Viaje.query.get_or_404(id)

    if request.method == 'POST':
        try:
            viaje.nombre = request.form.get('nombre')
            viaje.descripcion = request.form.get('descripcion')
            viaje.precio = float(request.form.get('precio'))
            viaje.fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date()
            viaje.duracion_min = int(request.form.get('duracion_min'))
            viaje.imagen_url = request.form.get('imagen_url')
            
            # Ajustar cupos (lógica simple: solo permitir aumentar cupos si ya hay reservas)
            nuevo_total = int(request.form.get('cupos_total'))
            diferencia = nuevo_total - viaje.cupos_total
            viaje.cupos_total = nuevo_total
            viaje.cupos_disp += diferencia
            
            viaje.categoria = request.form.get('categoria')
            viaje.descuento_pct = int(request.form.get('descuento_pct') or 0)
            
            db.session.commit()
            flash('Viaje actualizado exitosamente.', 'success')
            return redirect(url_for('admin.viajes'))
        except Exception as e:
            flash(f'Error al actualizar el viaje: {e}', 'error')

    return render_template('admin/viaje_form.html', viaje=viaje)

@admin_bp.route('/viajes/eliminar/<int:id>', methods=['POST'])
def eliminar_viaje(id):
    """Desactiva un viaje lógicamente en lugar de borrarlo físicamente para no romper reservas pasadas."""
    from app.extensions import db
    viaje = Viaje.query.get_or_404(id)
    viaje.activo = False
    db.session.commit()
@admin_bp.route('/reservas')
def reservas():
    """Listado maestro de todas las reservas en el sistema con datos para gráficas."""
    from app.models.reserva import Reserva
    from datetime import date
    todas_reservas = Reserva.query.order_by(Reserva.fecha_reserva.desc()).all()
    
    # Datos para Gráfica 1: Estado Operativo
    por_confirmar = len([r for r in todas_reservas if r.estado == 'pendiente'])
    hoy = len([r for r in todas_reservas if r.fecha_reserva.date() == date.today()])
    stats_operativas = [len(todas_reservas), por_confirmar, hoy]

    # Datos para Gráfica 2: Distribución de Estados
    confirmadas = len([r for r in todas_reservas if r.estado == 'confirmada'])
    canceladas = len([r for r in todas_reservas if r.estado == 'cancelada'])
    completadas = len([r for r in todas_reservas if r.estado == 'completada'])
    stats_estados = [len(todas_reservas), por_confirmar, confirmadas, canceladas, completadas]

    return render_template(
        'admin/reservas.html', 
        reservas=todas_reservas,
        stats_operativas=stats_operativas,
        stats_estados=stats_estados
    )

@admin_bp.route('/reservas/estado/<int:id>', methods=['POST'])
def cambiar_estado_reserva(id):
    """Permite al administrador forzar un cambio de estado en una reserva."""
    from app.models.reserva import Reserva
    from app.extensions import db
    reserva = Reserva.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado in ['pendiente', 'confirmada', 'cancelada', 'completada']:
        # Si se cancela una reserva confirmada, devolver cupos
        if reserva.estado == 'confirmada' and nuevo_estado == 'cancelada':
            reserva.viaje.cupos_disp += reserva.num_personas
            
        # Si se confirma una reserva pendiente o cancelada, descontar cupos
        elif reserva.estado in ['pendiente', 'cancelada'] and nuevo_estado == 'confirmada':
            if reserva.viaje.cupos_disp >= reserva.num_personas:
                reserva.viaje.cupos_disp -= reserva.num_personas
            else:
                flash('No hay suficientes cupos disponibles para confirmar esta reserva.', 'error')
                return redirect(url_for('admin.reservas'))
                
        reserva.estado = nuevo_estado
        db.session.commit()
        flash(f"Estado de la reserva {reserva.codigo_ref} actualizado a '{nuevo_estado}'.", "success")
@admin_bp.route('/reservas/editar/<int:id>', methods=['GET', 'POST'])
def editar_reserva(id):
    """Permite al administrador modificar detalles de una reserva."""
    from app.extensions import db
    from datetime import datetime
    reserva = Reserva.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Lógica de cupos: si cambia el número de personas
            nuevo_num_pax = int(request.form.get('num_personas'))
            diferencia = nuevo_num_pax - reserva.num_personas
            
            if diferencia > 0: # Quiere añadir más gente
                if reserva.viaje.cupos_disp >= diferencia:
                    reserva.viaje.cupos_disp -= diferencia
                else:
                    flash(f"No hay cupos suficientes para añadir {diferencia} personas más.", "error")
                    return redirect(url_for('admin.editar_reserva', id=id))
            elif diferencia < 0: # Quitó gente
                reserva.viaje.cupos_disp += abs(diferencia)
            
            reserva.num_personas = nuevo_num_pax
            reserva.fecha_viaje = datetime.strptime(request.form.get('fecha_viaje'), '%Y-%m-%d').date()
            reserva.estado = request.form.get('estado')
            reserva.total = float(request.form.get('total'))
            # Podríamos añadir un campo de notas en el modelo Reserva si existiera, 
            # por ahora guardamos los cambios básicos.
            
            db.session.commit()
            flash(f"Reserva {reserva.codigo_ref} actualizada correctamente.", "success")
            return redirect(url_for('admin.reservas'))
        except Exception as e:
            flash(f"Error al actualizar: {e}", "error")
            
    return render_template('admin/reserva_form.html', reserva=reserva)

@admin_bp.route('/reservas/eliminar/<int:id>', methods=['POST'])
def eliminar_reserva(id):
    """Elimina una reserva y devuelve los cupos si estaba confirmada."""
    from app.extensions import db
    reserva = Reserva.query.get_or_404(id)
    
    # Si estaba confirmada o pendiente, devolvemos los cupos
    if reserva.estado in ['confirmada', 'pendiente']:
        reserva.viaje.cupos_disp += reserva.num_personas
        
    db.session.delete(reserva)
    db.session.commit()
    flash("Reserva eliminada definitivamente. Los cupos han sido devueltos al viaje.", "success")
    return redirect(url_for('admin.reservas'))

@admin_bp.route('/reservas/reenviar/<int:id>', methods=['POST'])
def reenviar_confirmacion(id):
    """Reenvía el correo de confirmación al cliente."""
    from app.services.email_service import EmailService
    reserva = Reserva.query.get_or_404(id)
    
    success = EmailService.enviar_correo(
        destinatario=reserva.usuario.correo,
        asunto=f"Reenvío: Factura y Confirmación - Ref: {reserva.codigo_ref}",
        template='emails/factura.html',
        usuario=reserva.usuario,
        reserva=reserva
    )
    
    if success:
        flash(f"Correo de confirmación reenviado a {reserva.usuario.correo}", "success")
    else:
        flash("Hubo un problema al enviar el correo. Verifica la configuración SMTP.", "error")
        
    return redirect(url_for('admin.reservas'))
