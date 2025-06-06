from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'default':
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Register blueprints
    from app.controllers.main import main_bp
    from app.controllers.auth import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.threats import threats_bp
    from app.controllers.compliance import compliance_bp
    from app.controllers.vulnerabilities import vulnerabilities_bp
    from app.controllers.settings import settings_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(threats_bp, url_prefix='/threats')
    app.register_blueprint(compliance_bp, url_prefix='/compliance')
    app.register_blueprint(vulnerabilities_bp, url_prefix='/vulnerabilities')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Register error handlers
    from app.controllers.errors import register_error_handlers
    register_error_handlers(app)
    
    return app

