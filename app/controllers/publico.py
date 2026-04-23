from flask import Blueprint, render_template

publico_bp = Blueprint('publico', __name__)

@publico_bp.route('/')
def inicio():
    """
    Landing page (Página de Inicio).
    Muestra el Hero section, llamados a la acción y 
    los 3 viajes más recientes/destacados.
    """
    from app.models.viaje import Viaje
    # Obtener 3 viajes activos para destacar
    viajes_destacados = Viaje.query.filter_by(activo=True).limit(3).all()
    return render_template('publico/inicio.html', viajes=viajes_destacados)

@publico_bp.route('/nosotros')
def nosotros():
    """Página corporativa: Misión, visión, equipo."""
    return render_template('publico/nosotros.html')

@publico_bp.route('/contacto')
def contacto():
    """Página de contacto con formulario."""
    return render_template('publico/contacto.html')
