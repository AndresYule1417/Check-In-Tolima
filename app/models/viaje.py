from app.extensions import db
from datetime import datetime

class Viaje(db.Model):
    __tablename__ = 'viaje'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    duracion_min = db.Column(db.Integer) # duración en minutos
    imagen_url = db.Column(db.String(300))
    cupos_total = db.Column(db.Integer, default=10)
    cupos_disp = db.Column(db.Integer, default=10)
    categoria = db.Column(db.Enum('aventura', 'cultura', 'naturaleza', 'gastronomia', 'descanso', name='categoria_enum'))
    activo = db.Column(db.Boolean, default=True)
    descuento_pct = db.Column(db.Integer, default=0)
    incluye = db.Column(db.Text) # JSON string en SQLite por simplicidad
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    latitud = db.Column(db.Float, default=4.4389) # Default Ibagué
    longitud = db.Column(db.Float, default=-75.2322)

    def __repr__(self):
        return f'<Viaje {self.nombre} - {self.fecha_inicio}>'
