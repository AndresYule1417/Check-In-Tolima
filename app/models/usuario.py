from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.Enum('admin', 'usuario', name='roles_enum'), default='usuario', nullable=False)
    verificado = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    token_reset = db.Column(db.String(256), nullable=True)
    token_expira = db.Column(db.DateTime, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    def set_password(self, password):
        """Genera y almacena el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def get_token(self, salt):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id, salt=salt)

    @staticmethod
    def verify_token(token, salt, expires_sec=3600):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt=salt, max_age=expires_sec)
        except:
            return None
        return Usuario.query.get(user_id)

    def __repr__(self):
        return f'<Usuario {self.correo} - Rol: {self.rol}>'
