from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Organization, Asset
from app.models.security import Threat, Vulnerability, ComplianceAssessment, SecurityEvent
from app.utils.decorators import admin_required
from sqlalchemy import func
import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard route"""
    # Get organization data
    org = Organization.query.get(current_user.organization_id)
    
    # Get security metrics
    threats = Threat.query.filter_by(organization_id=current_user.organization_id).all()
    active_threats = [t for t in threats if t.status == 'active']
    
    vulnerabilities = Vulnerability.query.join(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).all()
    
    # Calculate security score (simplified version)
    total_assets = Asset.query.filter_by(organization_id=current_user.organization_id).count()
    critical_vulns = sum(1 for v in vulnerabilities if v.severity == 'critical')
    high_vulns = sum(1 for v in vulnerabilities if v.severity == 'high')
    medium_vulns = sum(1 for v in vulnerabilities if v.severity == 'medium')
    
    # Simple weighted score calculation
    if total_assets > 0:
        security_score = 100 - min(100, (critical_vulns * 10 + high_vulns * 5 + medium_vulns * 2) / total_assets)
    else:
        security_score = 100
    
    # Get compliance status
    compliance_assessments = ComplianceAssessment.query.filter_by(
        organization_id=current_user.organization_id
    ).all()
    
    total_controls = len(compliance_assessments)
    compliant_controls = sum(1 for a in compliance_assessments if a.status == 'compliant')
    
    compliance_percentage = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
    
    # Get recent security events
    recent_events = SecurityEvent.query.filter_by(
        organization_id=current_user.organization_id
    ).order_by(SecurityEvent.timestamp.desc()).limit(10).all()
    
    # Get security trends (last 30 days)
    thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    
    # Group events by day for the chart
    daily_events = db.session.query(
        func.date(SecurityEvent.timestamp).label('date'),
        func.count().label('count')
    ).filter(
        SecurityEvent.organization_id == current_user.organization_id,
        SecurityEvent.timestamp >= thirty_days_ago
    ).group_by(
        func.date(SecurityEvent.timestamp)
    ).order_by(
        func.date(SecurityEvent.timestamp)
    ).all()
    
    # Format for chart
    dates = [event.date.strftime('%Y-%m-%d') for event in daily_events]
    counts = [event.count for event in daily_events]
    
    return render_template(
        'dashboard/index.html',
        title='Dashboard',
        org=org,
        active_threats=active_threats,
        vulnerabilities=vulnerabilities,
        security_score=round(security_score),
        compliance_percentage=round(compliance_percentage),
        recent_events=recent_events,
        trend_dates=dates,
        trend_counts=counts
    )

@dashboard_bp.route('/overview')
@login_required
def overview():
    """Security overview route"""
    # Get asset statistics
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    asset_types = {}
    for asset in assets:
        if asset.asset_type in asset_types:
            asset_types[asset.asset_type] += 1
        else:
            asset_types[asset.asset_type] = 1
    
    # Get threat statistics
    threats = Threat.query.filter_by(organization_id=current_user.organization_id).all()
    threat_severity = {
        'critical': sum(1 for t in threats if t.severity == 'critical'),
        'high': sum(1 for t in threats if t.severity == 'high'),
        'medium': sum(1 for t in threats if t.severity == 'medium'),
        'low': sum(1 for t in threats if t.severity == 'low')
    }
    
    threat_status = {
        'active': sum(1 for t in threats if t.status == 'active'),
        'contained': sum(1 for t in threats if t.status == 'contained'),
        'resolved': sum(1 for t in threats if t.status == 'resolved'),
        'false_positive': sum(1 for t in threats if t.status == 'false_positive')
    }
    
    # Get vulnerability statistics
    vulnerabilities = Vulnerability.query.join(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).all()
    
    vuln_severity = {
        'critical': sum(1 for v in vulnerabilities if v.severity == 'critical'),
        'high': sum(1 for v in vulnerabilities if v.severity == 'high'),
        'medium': sum(1 for v in vulnerabilities if v.severity == 'medium'),
        'low': sum(1 for v in vulnerabilities if v.severity == 'low')
    }
    
    vuln_status = {
        'open': sum(1 for v in vulnerabilities if v.status == 'open'),
        'in_progress': sum(1 for v in vulnerabilities if v.status == 'in_progress'),
        'fixed': sum(1 for v in vulnerabilities if v.status == 'fixed'),
        'accepted_risk': sum(1 for v in vulnerabilities if v.status == 'accepted_risk'),
        'false_positive': sum(1 for v in vulnerabilities if v.status == 'false_positive')
    }
    
    return render_template(
        'dashboard/overview.html',
        title='Security Overview',
        asset_count=len(assets),
        asset_types=asset_types,
        threat_count=len(threats),
        threat_severity=threat_severity,
        threat_status=threat_status,
        vuln_count=len(vulnerabilities),
        vuln_severity=vuln_severity,
        vuln_status=vuln_status
    )

@dashboard_bp.route('/team')
@login_required
def team():
    """Team management route"""
    team_members = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    return render_template(
        'dashboard/team.html',
        title='Team Management',
        team_members=team_members
    )

@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile route"""
    from app.utils.forms import ProfileForm
    
    form = ProfileForm(obj=current_user)
    
    return render_template(
        'dashboard/profile.html',
        title='My Profile',
        form=form
    )

@dashboard_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile route"""
    from app.utils.forms import ProfileForm
    
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Your profile has been updated.', 'success')
    
    return redirect(url_for('dashboard.profile'))

@dashboard_bp.route('/activity')
@login_required
def activity():
    """User activity log route"""
    # Get login history
    login_history = LoginAttempt.query.filter_by(
        user_id=current_user.id
    ).order_by(LoginAttempt.timestamp.desc()).limit(50).all()
    
    return render_template(
        'dashboard/activity.html',
        title='Activity Log',
        login_history=login_history
    )

