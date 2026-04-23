from app import create_app
from app.extensions import db
from app.models.viaje import Viaje
from datetime import date, timedelta

def seed():
    app = create_app()
    with app.app_context():
        print("Limpiando base de datos para una carga limpia...")
        # Borramos lo que haya
        db.session.query(Viaje).delete()
        db.session.commit()

        print("Inyectando catálogo profesional de viajes...")
        
        viajes = [
            Viaje(
                nombre="Aventura Cocora",
                descripcion="Senderismo por el valle de las palmas más altas del mundo. Salento / Quindío.",
                precio=180000,
                categoria="aventura",
                imagen_url="/static/img/valle-cocora.jpg",
                fecha_inicio=date.today() + timedelta(days=10),
                duracion_min=480,
                cupos_total=20,
                cupos_disp=20,
                latitud=4.638,
                longitud=-75.487
            ),
            Viaje(
                nombre="Nevado del Tolima",
                descripcion="Ascenso épico al imponente Nevado del Tolima. Ibagué / Tolima.",
                precio=450000,
                categoria="aventura",
                imagen_url="/static/img/nevado.jpg",
                fecha_inicio=date.today() + timedelta(days=15),
                duracion_min=4320,
                cupos_total=12,
                cupos_disp=12,
                descuento_pct=10,
                latitud=4.659,
                longitud=-75.331
            ),
            Viaje(
                nombre="Ibagué City Tour",
                descripcion="Recorrido cultural por la Capital Musical de Colombia. Museos y gastronomía.",
                precio=85000,
                categoria="cultura",
                imagen_url="/static/img/Ibague.jpg",
                fecha_inicio=date.today() + timedelta(days=5),
                duracion_min=360,
                cupos_total=30,
                cupos_disp=30,
                latitud=4.438,
                longitud=-75.232
            ),
            Viaje(
                nombre="Represa de Prado",
                descripcion="Relajación y deportes acuáticos en el Mar Interior de Colombia. Prado / Tolima.",
                precio=120000,
                categoria="descanso",
                imagen_url="/static/img/represa-prado.jpg",
                fecha_inicio=date.today() + timedelta(days=20),
                duracion_min=1440,
                cupos_total=25,
                cupos_disp=25,
                latitud=3.748,
                longitud=-74.928
            )
        ]
        
        for v in viajes:
            db.session.add(v)
        
        db.session.commit()
        print("✅ ¡ÉXITO! El catálogo ha sido actualizado en la nube.")

if __name__ == "__main__":
    seed()
