from app import create_app
from app.extensions import db
from app.models.viaje import Viaje
from flask import url_for

app = create_app()
with app.app_context():
    mappings = {
        "Represa Prado": "/static/img/represa-prado.jpg",
        "Represa de Prado": "/static/img/represa-prado.jpg", # Posible variante
        "Aventura Cocora": "/static/img/valle-cocora.jpg",
        "Tour Ibagué": "/static/img/ibague.jpg",
        "Ecoturismo Valle": "/static/img/Ecoturismo.jpg"
    }
    
    for nombre, path in mappings.items():
        viaje = Viaje.query.filter(Viaje.nombre.like(f"%{nombre}%")).first()
        if viaje:
            viaje.imagen_url = path
            print(f"Actualizado: {viaje.nombre} -> {path}")
    
    db.session.commit()
    print("Base de datos actualizada con imágenes locales.")
