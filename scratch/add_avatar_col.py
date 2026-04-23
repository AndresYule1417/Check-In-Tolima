from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Añadir columna avatar_url si no existe (SQLite syntax)
        db.session.execute(text("ALTER TABLE usuario ADD COLUMN avatar_url VARCHAR(500)"))
        db.session.commit()
        print("Base de datos actualizada: Columna avatar_url añadida.")
    except Exception as e:
        print(f"Error o columna ya existe: {e}")
