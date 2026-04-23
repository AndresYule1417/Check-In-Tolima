from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Forzar la actualización de cualquier 'user' a 'usuario' usando SQL directo
        # para evitar que SQLAlchemy intente mapear el valor inválido primero.
        db.session.execute(text("UPDATE usuario SET rol = 'usuario' WHERE rol = 'user'"))
        db.session.commit()
        print("Limpieza de base de datos exitosa: Todos los roles 'user' corregidos a 'usuario'.")
    except Exception as e:
        print(f"Error al limpiar roles: {e}")
