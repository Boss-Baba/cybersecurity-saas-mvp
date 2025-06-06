from flask import render_template, current_app
import logging

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html', title='Bad Request'), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html', title='Unauthorized'), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html', title='Forbidden'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', title='Page Not Found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log the error
        current_app.logger.error(f'Server Error: {error}', exc_info=True)
        return render_template('errors/500.html', title='Server Error'), 500
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return render_template('errors/429.html', title='Too Many Requests'), 429

