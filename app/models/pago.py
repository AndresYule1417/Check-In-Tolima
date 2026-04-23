from app.extensions import db
from datetime import datetime

class Pago(db.Model):
    __tablename__ = 'pago'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)
    metodo = db.Column(db.String(50), nullable=False)
    referencia = db.Column(db.String(100))
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.Enum('simulado', 'aprobado', 'rechazado', name='estado_pago_enum'), default='simulado')
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    datos_demo = db.Column(db.Text) # JSON string para guardar datos adicionales de la simulación

    reserva = db.relationship('Reserva', backref=db.backref('pagos', lazy=True))

    def __repr__(self):
        return f'<Pago DEMO {self.id} - {self.estado}>'
