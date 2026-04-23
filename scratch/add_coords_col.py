from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE viaje ADD COLUMN latitud FLOAT DEFAULT 4.4389"))
        db.session.execute(text("ALTER TABLE viaje ADD COLUMN longitud FLOAT DEFAULT -75.2322"))
        db.session.commit()
        print("Base de datos actualizada: Columnas latitud y longitud añadidas.")
    except Exception as e:
        print(f"Error o columnas ya existen: {e}")
