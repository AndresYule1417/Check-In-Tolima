from app import create_app
from app.extensions import db
from app.models.viaje import Viaje

app = create_app()
with app.app_context():
    data = [
        ("Nevado", 4.6461, -75.3283),
        ("Prado", 3.7547, -74.9242),
        ("Cocora", 4.6361, -75.4851),
        ("Ibagué", 4.4389, -75.2322)
    ]
    
    for nombre, lat, lon in data:
        v = Viaje.query.filter(Viaje.nombre.like(f"%{nombre}%")).first()
        if v:
            v.latitud = lat
            v.longitud = lon
            print(f"Coordenadas actualizadas para {v.nombre}")
            
    db.session.commit()
