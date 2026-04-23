from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.viaje import Viaje
from app.models.reserva import Reserva
from app.models.pago import Pago
from app.services.email_service import EmailService

reservas_bp = Blueprint('reservas', __name__, url_prefix='/reservas')

@reservas_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    """
    Paso 1: Recibe los datos desde el detalle del viaje (personas, fecha),
    crea la reserva en estado 'pendiente' y redirige al checkout.
    """
    viaje_id = request.form.get('viaje_id')
    num_personas = int(request.form.get('personas', 1))
    
    viaje = Viaje.query.get_or_404(viaje_id)
    
    # Validar cupos
    if num_personas > viaje.cupos_disp:
        flash("No hay suficientes cupos disponibles para esta cantidad de personas.", "error")
        return redirect(url_for('viajes.detalle', id=viaje.id))
        
    # Calcular precio final con descuento
    precio_unitario = viaje.precio
    if viaje.descuento_pct > 0:
        precio_unitario = precio_unitario * (100 - viaje.descuento_pct) / 100
    total = precio_unitario * num_personas

    # Crear reserva
    nueva_reserva = Reserva(
        usuario_id=current_user.id,
        viaje_id=viaje.id,
        fecha_viaje=viaje.fecha_inicio,
        num_personas=num_personas,
        total=total,
        estado='pendiente'
    )
    
    db.session.add(nueva_reserva)
    db.session.commit()
    
    return redirect(url_for('reservas.checkout', codigo=nueva_reserva.codigo_ref))

@reservas_bp.route('/checkout/<codigo>', methods=['GET'])
@login_required
def checkout(codigo):
    """
    Paso 2: Muestra el formulario de pago DEMO y el resumen de compra.
    """
    reserva = Reserva.query.filter_by(codigo_ref=codigo, usuario_id=current_user.id).first_or_404()
    
    if reserva.estado != 'pendiente':
        flash("Esta reserva ya no está pendiente de pago.", "warning")
        return redirect(url_for('perfil.mi_perfil'))
        
    return render_template('reservas/checkout.html', reserva=reserva)

@reservas_bp.route('/procesar_pago', methods=['POST'])
@login_required
def procesar_pago():
    """
    Paso 3: Procesa el pago simulado. Si es exitoso, descuenta cupos y envía correo.
    """
    codigo_ref = request.form.get('codigo_ref')
    metodo = request.form.get('metodo_pago')
    num_tarjeta = request.form.get('numero_tarjeta', '')
    
    reserva = Reserva.query.filter_by(codigo_ref=codigo_ref, usuario_id=current_user.id).first_or_404()
    
    # Simulación simple: Fallar si la tarjeta termina en '0000'
    if num_tarjeta.endswith('0000'):
        flash("El pago ha sido rechazado por el banco (Simulación). Intenta con otra tarjeta.", "error")
        return redirect(url_for('reservas.checkout', codigo=codigo_ref))
        
    # Pago Exitoso Simulado
    import uuid
    ref_bancaria = f"TX-{uuid.uuid4().hex[:8].upper()}"
    
    nuevo_pago = Pago(
        reserva_id=reserva.id,
        metodo=metodo,
        referencia=ref_bancaria,
        monto=reserva.total,
        estado='aprobado'
    )
    
    # Actualizar estado de la reserva y método
    reserva.estado = 'confirmada'
    reserva.metodo_pago = 'tarjeta_demo' if metodo == 'tarjeta' else metodo
    
    # Descontar cupos del viaje (Bloqueo lógico)
    if reserva.viaje.cupos_disp >= reserva.num_personas:
        reserva.viaje.cupos_disp -= reserva.num_personas
    else:
        # Fallback de sobreventa (En un sistema real requeriría lock o rollback)
        pass

    db.session.add(nuevo_pago)
    db.session.commit()
    
    # Enviar Factura por Correo
    if EmailService.enviar_correo(
        destinatario=current_user.correo,
        asunto=f"Factura y Confirmación de Viaje {reserva.viaje.nombre} - Ref: {reserva.codigo_ref}",
        template='emails/factura.html',
        usuario=current_user,
        reserva=reserva
    ):
        reserva.factura_enviada = True
        db.session.commit()
    
    return redirect(url_for('reservas.confirmacion', codigo=reserva.codigo_ref))

@reservas_bp.route('/confirmacion/<codigo>')
@login_required
def confirmacion(codigo):
    """
    Paso 4: Pantalla final de éxito.
    """
    reserva = Reserva.query.filter_by(codigo_ref=codigo, usuario_id=current_user.id).first_or_404()
    return render_template('reservas/confirmacion.html', reserva=reserva)
