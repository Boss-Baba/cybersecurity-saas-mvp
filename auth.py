from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.models.user import User, LoginAttempt, Organization
from app.utils.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.email import send_password_reset_email, send_confirmation_email
from app.utils.security import generate_confirmation_token, confirm_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        # Record login attempt
        login_attempt = LoginAttempt(
            user_id=user.id if user else None,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=False
        )
        
        if user is None or not user.check_password(form.password.data):
            db.session.add(login_attempt)
            db.session.commit()
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            db.session.add(login_attempt)
            db.session.commit()
            flash('Your account has been disabled. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Successful login
        login_attempt.success = True
        db.session.add(login_attempt)
        
        # Update user's last login time
        user.update_last_login()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to the page the user was trying to access
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create organization first
        organization = Organization(
            name=form.company.data,
            domain=form.email.data.split('@')[1] if '@' in form.email.data else None,
            subscription_plan='trial',
            subscription_status='trial',
            subscription_expiry=datetime.datetime.utcnow() + datetime.timedelta(days=30)
        )
        db.session.add(organization)
        db.session.flush()  # Get the organization ID without committing
        
        # Create user
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            company=form.company.data,
            role='admin',  # First user is admin
            organization_id=organization.id
        )
        db.session.add(user)
        db.session.commit()
        
        # Send confirmation email
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        send_confirmation_email(user.email, confirm_url)
        
        flash('A confirmation email has been sent to your email address. Please check your inbox.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    """Email confirmation route"""
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(email=email).first_or_404()
    if user.email_confirmed:
        flash('Your account is already confirmed.', 'success')
    else:
        user.email_confirmed = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        flash('Your account has been confirmed. You can now log in.', 'success')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Password reset request route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_confirmation_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user.email, reset_url)
        
        # Always show this message even if email doesn't exist (security)
        flash('Check your email for instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    try:
        email = confirm_token(token)
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

