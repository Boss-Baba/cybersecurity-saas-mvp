from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Asset
from app.models.security import Threat
from app.utils.forms import ThreatFilterForm, ThreatActionForm
from app.utils.decorators import admin_required
from sqlalchemy import desc
import datetime

threats_bp = Blueprint('threats', __name__)

@threats_bp.route('/')
@login_required
def index():
    """Threats dashboard route"""
    form = ThreatFilterForm(request.args)
    
    # Base query
    query = Threat.query.filter_by(organization_id=current_user.organization_id)
    
    # Apply filters
    if form.validate():
        if form.severity.data and form.severity.data != 'all':
            query = query.filter(Threat.severity == form.severity.data)
        
        if form.status.data and form.status.data != 'all':
            query = query.filter(Threat.status == form.status.data)
        
        if form.threat_type.data and form.threat_type.data != 'all':
            query = query.filter(Threat.threat_type == form.threat_type.data)
        
        if form.source.data and form.source.data != 'all':
            query = query.filter(Threat.source == form.source.data)
        
        if form.date_from.data:
            query = query.filter(Threat.detected_at >= form.date_from.data)
        
        if form.date_to.data:
            query = query.filter(Threat.detected_at <= form.date_to.data)
    
    # Sort
    sort_by = request.args.get('sort_by', 'detected_at')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    if sort_dir == 'desc':
        query = query.order_by(desc(getattr(Threat, sort_by)))
    else:
        query = query.order_by(getattr(Threat, sort_by))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    threats = pagination.items
    
    # Get assets and users for display
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    # Statistics
    total_threats = query.count()
    critical_threats = query.filter(Threat.severity == 'critical').count()
    high_threats = query.filter(Threat.severity == 'high').count()
    medium_threats = query.filter(Threat.severity == 'medium').count()
    low_threats = query.filter(Threat.severity == 'low').count()
    
    active_threats = query.filter(Threat.status == 'active').count()
    contained_threats = query.filter(Threat.status == 'contained').count()
    resolved_threats = query.filter(Threat.status == 'resolved').count()
    
    return render_template(
        'threats/index.html',
        title='Threat Detection',
        threats=threats,
        pagination=pagination,
        form=form,
        assets=assets,
        users=users,
        total_threats=total_threats,
        critical_threats=critical_threats,
        high_threats=high_threats,
        medium_threats=medium_threats,
        low_threats=low_threats,
        active_threats=active_threats,
        contained_threats=contained_threats,
        resolved_threats=resolved_threats,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@threats_bp.route('/<uuid>')
@login_required
def view(uuid):
    """View threat details route"""
    threat = Threat.query.filter_by(
        uuid=uuid, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    action_form = ThreatActionForm()
    
    # Get related assets and users for assignment
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    return render_template(
        'threats/view.html',
        title=f'Threat: {threat.name}',
        threat=threat,
        action_form=action_form,
        assets=assets,
        users=users
    )

@threats_bp.route('/<uuid>/update', methods=['POST'])
@login_required
def update(uuid):
    """Update threat status route"""
    threat = Threat.query.filter_by(
        uuid=uuid, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    form = ThreatActionForm()
    if form.validate_on_submit():
        if form.action.data == 'contain':
            threat.status = 'contained'
            flash('Threat has been marked as contained.', 'success')
        
        elif form.action.data == 'resolve':
            threat.status = 'resolved'
            threat.resolved_at = datetime.datetime.utcnow()
            flash('Threat has been marked as resolved.', 'success')
        
        elif form.action.data == 'false_positive':
            threat.status = 'false_positive'
            flash('Threat has been marked as a false positive.', 'success')
        
        elif form.action.data == 'reactivate':
            threat.status = 'active'
            flash('Threat has been reactivated.', 'warning')
        
        if form.assign_to.data:
            user = User.query.get(form.assign_to.data)
            if user and user.organization_id == current_user.organization_id:
                threat.assigned_to = user.id
                flash(f'Threat has been assigned to {user.first_name} {user.last_name}.', 'info')
        
        if form.notes.data:
            # In a real implementation, we would add this to a threat notes table
            pass
        
        db.session.commit()
    
    return redirect(url_for('threats.view', uuid=threat.uuid))

@threats_bp.route('/simulate', methods=['GET', 'POST'])
@login_required
@admin_required
def simulate():
    """Simulate a threat for testing (admin only)"""
    from app.utils.forms import ThreatSimulationForm
    
    form = ThreatSimulationForm()
    
    # Get assets for the form
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    form.asset_id.choices = [(a.id, a.name) for a in assets]
    
    if form.validate_on_submit():
        asset = Asset.query.get(form.asset_id.data)
        
        # Create simulated threat
        threat = Threat(
            name=form.name.data,
            description=form.description.data,
            threat_type=form.threat_type.data,
            severity=form.severity.data,
            status='active',
            source=form.source.data,
            detection_method='manual',
            organization_id=current_user.organization_id,
            asset_id=asset.id if asset else None
        )
        
        db.session.add(threat)
        db.session.commit()
        
        flash('Simulated threat has been created.', 'success')
        return redirect(url_for('threats.view', uuid=threat.uuid))
    
    return render_template(
        'threats/simulate.html',
        title='Simulate Threat',
        form=form
    )

@threats_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for threat statistics"""
    # Get threat statistics for charts
    threats = Threat.query.filter_by(organization_id=current_user.organization_id).all()
    
    # By severity
    severity_stats = {
        'critical': sum(1 for t in threats if t.severity == 'critical'),
        'high': sum(1 for t in threats if t.severity == 'high'),
        'medium': sum(1 for t in threats if t.severity == 'medium'),
        'low': sum(1 for t in threats if t.severity == 'low')
    }
    
    # By status
    status_stats = {
        'active': sum(1 for t in threats if t.status == 'active'),
        'contained': sum(1 for t in threats if t.status == 'contained'),
        'resolved': sum(1 for t in threats if t.status == 'resolved'),
        'false_positive': sum(1 for t in threats if t.status == 'false_positive')
    }
    
    # By type
    type_stats = {}
    for threat in threats:
        if threat.threat_type in type_stats:
            type_stats[threat.threat_type] += 1
        else:
            type_stats[threat.threat_type] = 1
    
    # By source
    source_stats = {}
    for threat in threats:
        if threat.source in source_stats:
            source_stats[threat.source] += 1
        else:
            source_stats[threat.source] = 1
    
    # By time (last 30 days)
    thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    recent_threats = [t for t in threats if t.detected_at >= thirty_days_ago]
    
    # Group by day
    daily_threats = {}
    for threat in recent_threats:
        day = threat.detected_at.strftime('%Y-%m-%d')
        if day in daily_threats:
            daily_threats[day] += 1
        else:
            daily_threats[day] = 1
    
    # Fill in missing days
    for i in range(30):
        day = (datetime.datetime.utcnow() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        if day not in daily_threats:
            daily_threats[day] = 0
    
    # Sort by date
    daily_threats = {k: daily_threats[k] for k in sorted(daily_threats.keys())}
    
    return jsonify({
        'severity': severity_stats,
        'status': status_stats,
        'type': type_stats,
        'source': source_stats,
        'daily': daily_threats
    })

