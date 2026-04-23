import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
# Importamos todos los modelos necesarios para que SQLAlchemy entienda las relaciones
from app.models.viaje import Viaje
from app.models.usuario import Usuario

# ---------------------------------------------------------
# PEGA AQUÍ TU URL EXTERNA DE RENDER
# ---------------------------------------------------------
DATABASE_URL = "postgresql://checkin_db_ko3r_user:xpplwgDNjU076EkrKu5ObfWV1JsFUjRP@dpg-d7krkp7lk1mc73bd76jg-a.oregon-postgres.render.com/checkin_db_ko3r"

def seed():
    if "PEGAR_AQUI" in DATABASE_URL:
        print("❌ ERROR: No has pegado la URL de Render.")
        return

    print(f"Conectando a Render...")
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Aseguramos que las tablas existan en Postgres
        from app.extensions import db
        print("Sincronizando tablas en la nube...")
        
        print("Limpiando viajes viejos...")
        session.query(Viaje).delete()
        session.commit()

        print("Inyectando catálogo profesional...")
        
        viajes = [
            Viaje(nombre="Aventura Cocora", descripcion="Valle de las palmas gigantes. Quindío.", precio=180000, categoria="aventura", imagen_url="/static/img/valle-cocora.jpg", fecha_inicio=date.today() + timedelta(days=10), duracion_min=480, cupos_total=20, cupos_disp=20),
            Viaje(nombre="Nevado del Tolima", descripcion="Ascenso de alta montaña. Ibagué.", precio=450000, categoria="aventura", imagen_url="/static/img/nevado.jpg", fecha_inicio=date.today() + timedelta(days=15), duracion_min=4320, cupos_total=12, cupos_disp=12, descuento_pct=10),
            Viaje(nombre="Ibagué City Tour", descripcion="Recorrido cultural. Capital Musical.", precio=85000, categoria="cultura", imagen_url="/static/img/Ibague.jpg", fecha_inicio=date.today() + timedelta(days=5), duracion_min=360, cupos_total=30, cupos_disp=30),
            Viaje(nombre="Represa de Prado", descripcion="Mar interior de Colombia. Tolima.", precio=120000, categoria="descanso", imagen_url="/static/img/represa-prado.jpg", fecha_inicio=date.today() + timedelta(days=20), duracion_min=1440, cupos_total=25, cupos_disp=25)
        ]
        
        session.add_all(viajes)
        session.commit()
        print("✅ ¡ÉXITO TOTAL! Los viajes están en vivo en Render.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
