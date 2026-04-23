from flask import Flask, redirect, url_for, render_template
from config import Config
from app.extensions import db, login_manager, mail
from datetime import date

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Registrar Blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.viajes import viajes_bp
    from app.controllers.perfil import perfil_bp
    from app.controllers.admin import admin_bp
    from app.controllers.publico import publico_bp
    from app.controllers.reservas import reservas_bp

    app.register_blueprint(publico_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(viajes_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reservas_bp)

    # Manejadores de Errores
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Inicializar base de datos y datos semilla
    with app.app_context():
        # Importar modelos ANTES de create_all para que SQLAlchemy los detecte
        from app.models.usuario import Usuario
        from app.models.viaje import Viaje
        from app.models.reserva import Reserva
        from app.models.pago import Pago
        
        db.create_all()
        _insertar_datos_semilla()

    return app

def _insertar_datos_semilla():
    """Inserta datos demo si la base de datos está vacía para pruebas visuales."""
    from app.models.viaje import Viaje
    
    # Importante: Como Viaje aún no está creado completo, ponemos esto en un try
    try:
        if not Viaje.query.first():
            viajes_demo = [
                Viaje(
                    nombre='Nevado del Tolima',
                    descripcion='Aventura extrema en el imponente Nevado del Tolima. Incluye equipo y guía profesional.',
                    precio=450000.00,
                    fecha_inicio=date(2024, 7, 15),
                    duracion_min=2880, # 2 días
                    imagen_url='/static/img/nevado.jpg',
                    cupos_total=10,
                    cupos_disp=10,
                    categoria='aventura',
                    descuento_pct=10,
                    activo=True
                ),
                Viaje(
                    nombre='Represa de Prado',
                    descripcion='Descanso y deportes acuáticos en el "Mar Interior" de Colombia.',
                    precio=120000.00,
                    fecha_inicio=date(2024, 8, 5),
                    duracion_min=720, # Medio día
                    imagen_url='/static/img/represa-prado.jpg',
                    cupos_total=20,
                    cupos_disp=5,
                    categoria='descanso',
                    activo=True
                )
            ]
            db.session.add_all(viajes_demo)
            db.session.commit()
            print("Datos semilla de viajes insertados.")
    except Exception as e:
        print(f"Nota: No se insertaron datos semilla aún. {e}")
