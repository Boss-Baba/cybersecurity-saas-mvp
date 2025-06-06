from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin', 'superadmin'
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization', back_populates='users')
    
    # Security settings
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    
    # Login history
    login_attempts = db.relationship('LoginAttempt', back_populates='user', lazy='dynamic')
    
    def __init__(self, email, username, password, **kwargs):
        self.email = email.lower()
        self.username = username
        self.set_password(password)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Set password hash for user"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def has_role(self, role):
        """Check if user has specified role"""
        return self.role == role
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role in ['admin', 'superadmin']
    
    def __repr__(self):
        return f'<User {self.username}>'


class Organization(db.Model):
    """Organization model for multi-tenant support"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100), nullable=True)
    subscription_plan = db.Column(db.String(20), default='free')  # 'free', 'essentials', 'professional', 'enterprise'
    subscription_status = db.Column(db.String(20), default='active')  # 'active', 'trial', 'expired', 'cancelled'
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='organization')
    assets = db.relationship('Asset', back_populates='organization')
    
    def __repr__(self):
        return f'<Organization {self.name}>'


class LoginAttempt(db.Model):
    """Model to track login attempts for security monitoring"""
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='login_attempts')
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    success = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LoginAttempt {self.user_id} {self.success}>'


class Asset(db.Model):
    """Model for tracking organization assets"""
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # 'endpoint', 'server', 'cloud', 'network', 'application'
    ip_address = db.Column(db.String(45), nullable=True)
    hostname = db.Column(db.String(100), nullable=True)
    os_type = db.Column(db.String(50), nullable=True)
    os_version = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'decommissioned'
    criticality = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    last_scan = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization', back_populates='assets')
    vulnerabilities = db.relationship('Vulnerability', back_populates='asset')
    
    def __repr__(self):
        return f'<Asset {self.name}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

