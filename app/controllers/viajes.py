from flask import Blueprint, render_template

viajes_bp = Blueprint('viajes', __name__, url_prefix='/viajes')

@viajes_bp.route('/')
def catalogo():
    from flask import request
    from app.models.viaje import Viaje
    
    categoria = request.args.get('categoria')
    busqueda = request.args.get('q')
    
    query = Viaje.query.filter_by(activo=True)
    
    if categoria and categoria != 'todos':
        query = query.filter_by(categoria=categoria.lower())
        
    if busqueda:
        query = query.filter(Viaje.nombre.ilike(f'%{busqueda}%') | Viaje.descripcion.ilike(f'%{busqueda}%'))
        
    viajes = query.all()
    return render_template('viajes/catalogo.html', viajes=viajes, categoria_actual=categoria)

@viajes_bp.route('/<int:id>')
def detalle(id):
    """
    Vista detallada de un viaje específico.
    """
    from app.models.viaje import Viaje
    viaje = Viaje.query.get_or_404(id)
    return render_template('viajes/detalle.html', viaje=viaje)
