from app import create_app
from app.extensions import db
from app.models.viaje import Viaje

app = create_app()
with app.app_context():
    # Corregir Tour Ibagué (I mayúscula)
    viaje = Viaje.query.filter(Viaje.nombre.like("%Tour Ibagué%")).first()
    if viaje:
        viaje.imagen_url = "/static/img/Ibague.jpg"
        print(f"Actualizado: {viaje.nombre} -> /static/img/Ibague.jpg")
    
    # Por si acaso la portada se usa en algún viaje (ej. Nevado)
    nevado = Viaje.query.filter(Viaje.nombre.like("%Nevado del Tolima%")).first()
    if nevado:
        nevado.imagen_url = "/static/img/portada..png"
        print(f"Actualizado: {nevado.nombre} -> /static/img/portada..png")

    db.session.commit()
    print("Correcciones de nombres de archivos aplicadas.")
