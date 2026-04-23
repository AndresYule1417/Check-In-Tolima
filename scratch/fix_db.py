from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Actualizar todos los roles 'user' a 'usuario' usando SQL crudo para evitar el error del Enum de SQLAlchemy
        db.session.execute(text("UPDATE usuario SET rol = 'usuario' WHERE rol = 'user'"))
        db.session.commit()
        print("Base de datos actualizada: 'user' -> 'usuario'")
    except Exception as e:
        print(f"Error al actualizar la base de datos: {e}")
