from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('main/index.html', title='Welcome')

@main_bp.route('/features')
def features():
    """Features page route"""
    return render_template('main/features.html', title='Features')

@main_bp.route('/pricing')
def pricing():
    """Pricing page route"""
    return render_template('main/pricing.html', title='Pricing')

@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('main/about.html', title='About Us')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route"""
    from app.utils.forms import ContactForm
    from app.utils.email import send_contact_email
    
    form = ContactForm()
    if form.validate_on_submit():
        send_contact_email(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        return render_template('main/contact_success.html', title='Message Sent')
    
    return render_template('main/contact.html', title='Contact Us', form=form)

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page route"""
    return render_template('main/privacy.html', title='Privacy Policy')

@main_bp.route('/terms')
def terms():
    """Terms of service page route"""
    return render_template('main/terms.html', title='Terms of Service')

@main_bp.route('/security')
def security():
    """Security page route"""
    return render_template('main/security.html', title='Security')

@main_bp.route('/demo')
def demo():
    """Demo request page route"""
    from app.utils.forms import DemoRequestForm
    from app.utils.email import send_demo_request_email
    
    form = DemoRequestForm()
    if form.validate_on_submit():
        send_demo_request_email(
            name=form.name.data,
            email=form.email.data,
            company=form.company.data,
            phone=form.phone.data,
            message=form.message.data
        )
        return render_template('main/demo_success.html', title='Demo Requested')
    
    return render_template('main/demo.html', title='Request a Demo', form=form)

