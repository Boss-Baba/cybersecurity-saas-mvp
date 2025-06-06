from functools import wraps
from flask import flash, redirect, url_for, request, abort
from flask_login import current_user

def admin_required(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(role):
    """Decorator for routes that require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_role(role):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def confirmed_email_required(f):
    """Decorator for routes that require confirmed email"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.email_confirmed:
            flash('Please confirm your email address before accessing this page.', 'warning')
            return redirect(url_for('auth.unconfirmed'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def subscription_required(plan_level):
    """Decorator for routes that require specific subscription level"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            from app.models.user import Organization
            org = Organization.query.get(current_user.organization_id)
            
            # Define plan levels
            plan_levels = {
                'free': 0,
                'essentials': 1,
                'professional': 2,
                'enterprise': 3
            }
            
            required_level = plan_levels.get(plan_level, 0)
            current_level = plan_levels.get(org.subscription_plan, 0)
            
            if current_level < required_level:
                flash(f'This feature requires a {plan_level.capitalize()} subscription.', 'warning')
                return redirect(url_for('settings.subscription'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def api_key_required(f):
    """Decorator for API routes that require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401
        
        # In a real implementation, validate the API key against the database
        # For the MVP, we'll use a simple check
        if not api_key.startswith('csp_'):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(limit=100, per=60):
    """Decorator for rate limiting API requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            import time
            from app import redis_client
            
            # In a real implementation, use Redis or similar for rate limiting
            # For the MVP, we'll just pass through
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

