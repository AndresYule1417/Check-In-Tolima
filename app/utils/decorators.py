from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorador personalizado que verifica si el usuario actual
    tiene el rol de 'admin'. De lo contrario, retorna un error
    o redirige al inicio.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for('auth.login'))
            
        if current_user.rol != 'admin':
            flash("No tienes permisos suficientes para acceder a esta zona.", "error")
            return redirect(url_for('viajes.catalogo'))
            
        return f(*args, **kwargs)
    return decorated_function
