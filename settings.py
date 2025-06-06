from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Organization, Asset
from app.utils.forms import OrganizationSettingsForm, UserInviteForm, AssetForm
from app.utils.decorators import admin_required
from app.utils.email import send_invitation_email
from app.utils.security import generate_confirmation_token
import datetime
import uuid

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
def index():
    """Settings dashboard route"""
    return render_template(
        'settings/index.html',
        title='Settings'
    )

@settings_bp.route('/organization', methods=['GET', 'POST'])
@login_required
@admin_required
def organization():
    """Organization settings route (admin only)"""
    org = Organization.query.get(current_user.organization_id)
    form = OrganizationSettingsForm(obj=org)
    
    if form.validate_on_submit():
        org.name = form.name.data
        org.domain = form.domain.data
        
        db.session.commit()
        flash('Organization settings have been updated.', 'success')
        return redirect(url_for('settings.organization'))
    
    return render_template(
        'settings/organization.html',
        title='Organization Settings',
        form=form,
        org=org
    )

@settings_bp.route('/users')
@login_required
@admin_required
def users():
    """User management route (admin only)"""
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    invite_form = UserInviteForm()
    
    return render_template(
        'settings/users.html',
        title='User Management',
        users=users,
        invite_form=invite_form
    )

@settings_bp.route('/users/invite', methods=['POST'])
@login_required
@admin_required
def invite_user():
    """Invite user route (admin only)"""
    form = UserInviteForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('settings.users'))
        
        # Generate a random password for the new user
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Create user
        user = User(
            email=form.email.data,
            username=form.email.data.split('@')[0],  # Simple username from email
            password=temp_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            organization_id=current_user.organization_id,
            is_active=True,
            email_confirmed=False
        )
        db.session.add(user)
        db.session.commit()
        
        # Send invitation email
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        send_invitation_email(
            user.email,
            confirm_url,
            current_user.first_name,
            current_user.last_name,
            Organization.query.get(current_user.organization_id).name,
            temp_password
        )
        
        flash(f'Invitation sent to {user.email}.', 'success')
        return redirect(url_for('settings.users'))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('settings.users'))

@settings_bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status route (admin only)"""
    user = User.query.filter_by(
        id=user_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    # Don't allow deactivating yourself
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('settings.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('settings.users'))

@settings_bp.route('/users/<int:user_id>/change_role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """Change user role route (admin only)"""
    user = User.query.filter_by(
        id=user_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    # Don't allow changing your own role
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('settings.users'))
    
    new_role = request.form.get('role')
    if new_role in ['user', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'User {user.email} role has been changed to {new_role}.', 'success')
    else:
        flash('Invalid role.', 'danger')
    
    return redirect(url_for('settings.users'))

@settings_bp.route('/assets')
@login_required
def assets():
    """Asset management route"""
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    form = AssetForm()
    
    return render_template(
        'settings/assets.html',
        title='Asset Management',
        assets=assets,
        form=form
    )

@settings_bp.route('/assets/add', methods=['POST'])
@login_required
def add_asset():
    """Add asset route"""
    form = AssetForm()
    if form.validate_on_submit():
        asset = Asset(
            name=form.name.data,
            asset_type=form.asset_type.data,
            ip_address=form.ip_address.data,
            hostname=form.hostname.data,
            os_type=form.os_type.data,
            os_version=form.os_version.data,
            criticality=form.criticality.data,
            organization_id=current_user.organization_id
        )
        db.session.add(asset)
        db.session.commit()
        
        flash(f'Asset {asset.name} has been added.', 'success')
        return redirect(url_for('settings.assets'))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('settings.assets'))

@settings_bp.route('/assets/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    """Edit asset route"""
    asset = Asset.query.filter_by(
        id=asset_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    form = AssetForm(obj=asset)
    
    if form.validate_on_submit():
        asset.name = form.name.data
        asset.asset_type = form.asset_type.data
        asset.ip_address = form.ip_address.data
        asset.hostname = form.hostname.data
        asset.os_type = form.os_type.data
        asset.os_version = form.os_version.data
        asset.criticality = form.criticality.data
        
        db.session.commit()
        flash(f'Asset {asset.name} has been updated.', 'success')
        return redirect(url_for('settings.assets'))
    
    return render_template(
        'settings/edit_asset.html',
        title=f'Edit Asset: {asset.name}',
        asset=asset,
        form=form
    )

@settings_bp.route('/assets/<int:asset_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_asset(asset_id):
    """Delete asset route (admin only)"""
    asset = Asset.query.filter_by(
        id=asset_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    # Check if asset has vulnerabilities
    if asset.vulnerabilities:
        flash(f'Cannot delete asset {asset.name} because it has associated vulnerabilities.', 'danger')
        return redirect(url_for('settings.assets'))
    
    db.session.delete(asset)
    db.session.commit()
    
    flash(f'Asset {asset.name} has been deleted.', 'success')
    return redirect(url_for('settings.assets'))

@settings_bp.route('/subscription')
@login_required
@admin_required
def subscription():
    """Subscription management route (admin only)"""
    org = Organization.query.get(current_user.organization_id)
    
    return render_template(
        'settings/subscription.html',
        title='Subscription Management',
        org=org
    )

@settings_bp.route('/api-keys')
@login_required
@admin_required
def api_keys():
    """API key management route (admin only)"""
    # In a real implementation, this would manage API keys for integration
    
    return render_template(
        'settings/api_keys.html',
        title='API Keys'
    )

@settings_bp.route('/notifications')
@login_required
def notifications():
    """Notification settings route"""
    # In a real implementation, this would manage notification preferences
    
    return render_template(
        'settings/notifications.html',
        title='Notification Settings'
    )

