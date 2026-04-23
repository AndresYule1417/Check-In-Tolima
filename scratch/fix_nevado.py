from app import create_app
from app.extensions import db
from app.models.viaje import Viaje

app = create_app()
with app.app_context():
    viaje = Viaje.query.filter(Viaje.nombre.like("%Nevado del Tolima%")).first()
    if viaje:
        viaje.imagen_url = "/static/img/nevado.jpg"
        print(f"Actualizado: {viaje.nombre} -> /static/img/nevado.jpg")
    
    db.session.commit()
    print("Base de datos actualizada.")
