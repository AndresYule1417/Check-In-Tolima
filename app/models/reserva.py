from app.extensions import db
from datetime import datetime
import string
import random

def generar_codigo_reserva():
    """Genera un código de referencia único tipo CKT-XXXXXX"""
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=6))
    return f'CKT-{codigo}'

class Reserva(db.Model):
    __tablename__ = 'reserva'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_viaje = db.Column(db.Date, nullable=False)
    num_personas = db.Column(db.Integer, default=1, nullable=False)
    notas = db.Column(db.Text)
    estado = db.Column(db.Enum('pendiente', 'confirmada', 'cancelada', 'completada', name='estado_reserva_enum'), default='pendiente')
    metodo_pago = db.Column(db.Enum('efectivo', 'transferencia', 'nequi', 'daviplata', 'pse', 'tarjeta_demo', name='metodo_pago_enum'))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    codigo_ref = db.Column(db.String(20), unique=True, default=generar_codigo_reserva)
    factura_enviada = db.Column(db.Boolean, default=False)

    # Relaciones para acceder fácilmente a los objetos relacionados
    usuario = db.relationship('Usuario', backref='reservas')
    viaje = db.relationship('Viaje', backref='reservas')

    def __repr__(self):
        return f'<Reserva {self.codigo_ref} - {self.estado}>'
