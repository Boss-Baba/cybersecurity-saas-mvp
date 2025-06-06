from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Asset
from app.models.security import Vulnerability
from app.utils.forms import VulnerabilityFilterForm, VulnerabilityActionForm
from app.utils.decorators import admin_required
from sqlalchemy import desc
import datetime

vulnerabilities_bp = Blueprint('vulnerabilities', __name__)

@vulnerabilities_bp.route('/')
@login_required
def index():
    """Vulnerabilities dashboard route"""
    form = VulnerabilityFilterForm(request.args)
    
    # Base query - join with Asset to filter by organization
    query = Vulnerability.query.join(Asset).filter(Asset.organization_id == current_user.organization_id)
    
    # Apply filters
    if form.validate():
        if form.severity.data and form.severity.data != 'all':
            query = query.filter(Vulnerability.severity == form.severity.data)
        
        if form.status.data and form.status.data != 'all':
            query = query.filter(Vulnerability.status == form.status.data)
        
        if form.asset_id.data:
            query = query.filter(Vulnerability.asset_id == form.asset_id.data)
        
        if form.date_from.data:
            query = query.filter(Vulnerability.detected_at >= form.date_from.data)
        
        if form.date_to.data:
            query = query.filter(Vulnerability.detected_at <= form.date_to.data)
    
    # Sort
    sort_by = request.args.get('sort_by', 'detected_at')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    if sort_dir == 'desc':
        query = query.order_by(desc(getattr(Vulnerability, sort_by)))
    else:
        query = query.order_by(getattr(Vulnerability, sort_by))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    vulnerabilities = pagination.items
    
    # Get assets and users for display
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    # Update form choices for assets
    form.asset_id.choices = [('', 'All Assets')] + [(a.id, a.name) for a in assets]
    
    # Statistics
    total_vulns = query.count()
    critical_vulns = query.filter(Vulnerability.severity == 'critical').count()
    high_vulns = query.filter(Vulnerability.severity == 'high').count()
    medium_vulns = query.filter(Vulnerability.severity == 'medium').count()
    low_vulns = query.filter(Vulnerability.severity == 'low').count()
    
    open_vulns = query.filter(Vulnerability.status == 'open').count()
    in_progress_vulns = query.filter(Vulnerability.status == 'in_progress').count()
    fixed_vulns = query.filter(Vulnerability.status == 'fixed').count()
    
    return render_template(
        'vulnerabilities/index.html',
        title='Vulnerability Management',
        vulnerabilities=vulnerabilities,
        pagination=pagination,
        form=form,
        assets=assets,
        users=users,
        total_vulns=total_vulns,
        critical_vulns=critical_vulns,
        high_vulns=high_vulns,
        medium_vulns=medium_vulns,
        low_vulns=low_vulns,
        open_vulns=open_vulns,
        in_progress_vulns=in_progress_vulns,
        fixed_vulns=fixed_vulns,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@vulnerabilities_bp.route('/<uuid>')
@login_required
def view(uuid):
    """View vulnerability details route"""
    vulnerability = Vulnerability.query.filter_by(uuid=uuid).join(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).first_or_404()
    
    action_form = VulnerabilityActionForm()
    
    # Get users for assignment
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    return render_template(
        'vulnerabilities/view.html',
        title=f'Vulnerability: {vulnerability.title}',
        vulnerability=vulnerability,
        action_form=action_form,
        users=users
    )

@vulnerabilities_bp.route('/<uuid>/update', methods=['POST'])
@login_required
def update(uuid):
    """Update vulnerability status route"""
    vulnerability = Vulnerability.query.filter_by(uuid=uuid).join(Asset).filter(
        Asset.organization_id == current_user.organization_id
    ).first_or_404()
    
    form = VulnerabilityActionForm()
    if form.validate_on_submit():
        if form.action.data == 'start':
            vulnerability.status = 'in_progress'
            flash('Vulnerability has been marked as in progress.', 'info')
        
        elif form.action.data == 'fix':
            vulnerability.status = 'fixed'
            vulnerability.fixed_at = datetime.datetime.utcnow()
            flash('Vulnerability has been marked as fixed.', 'success')
        
        elif form.action.data == 'accept_risk':
            vulnerability.status = 'accepted_risk'
            flash('Vulnerability has been marked as accepted risk.', 'warning')
        
        elif form.action.data == 'false_positive':
            vulnerability.status = 'false_positive'
            flash('Vulnerability has been marked as a false positive.', 'info')
        
        elif form.action.data == 'reopen':
            vulnerability.status = 'open'
            vulnerability.fixed_at = None
            flash('Vulnerability has been reopened.', 'warning')
        
        if form.assign_to.data:
            user = User.query.get(form.assign_to.data)
            if user and user.organization_id == current_user.organization_id:
                vulnerability.assigned_to = user.id
                flash(f'Vulnerability has been assigned to {user.first_name} {user.last_name}.', 'info')
        
        if form.notes.data:
            # In a real implementation, we would add this to a vulnerability notes table
            pass
        
        db.session.commit()
    
    return redirect(url_for('vulnerabilities.view', uuid=vulnerability.uuid))

@vulnerabilities_bp.route('/scan', methods=['GET', 'POST'])
@login_required
@admin_required
def scan():
    """Run vulnerability scan route (admin only)"""
    from app.utils.forms import VulnerabilityScanForm
    
    form = VulnerabilityScanForm()
    
    # Get assets for the form
    assets = Asset.query.filter_by(organization_id=current_user.organization_id).all()
    form.asset_ids.choices = [(a.id, a.name) for a in assets]
    
    if form.validate_on_submit():
        selected_assets = [Asset.query.get(id) for id in form.asset_ids.data]
        
        # In a real implementation, this would trigger an actual scan
        # For the MVP, we'll simulate finding vulnerabilities
        
        # Sample vulnerabilities to simulate
        sample_vulns = [
            {
                'cve_id': 'CVE-2025-1234',
                'title': 'Remote Code Execution in Apache',
                'description': 'A vulnerability in Apache HTTP Server allows remote attackers to execute arbitrary code.',
                'severity': 'critical',
                'cvss_score': 9.8,
                'remediation': 'Update to Apache 2.6.2 or later.'
            },
            {
                'cve_id': 'CVE-2025-5678',
                'title': 'SQL Injection in WordPress Plugin',
                'description': 'A SQL injection vulnerability in a popular WordPress plugin allows attackers to access sensitive data.',
                'severity': 'high',
                'cvss_score': 8.5,
                'remediation': 'Update the plugin to the latest version or remove it if unused.'
            },
            {
                'cve_id': 'CVE-2025-9012',
                'title': 'Cross-Site Scripting in Web Application',
                'description': 'A cross-site scripting vulnerability allows attackers to inject malicious scripts.',
                'severity': 'medium',
                'cvss_score': 6.4,
                'remediation': 'Implement proper input validation and output encoding.'
            },
            {
                'cve_id': 'CVE-2025-3456',
                'title': 'Outdated SSL/TLS Configuration',
                'description': 'The system is using outdated SSL/TLS protocols that are vulnerable to known attacks.',
                'severity': 'medium',
                'cvss_score': 5.9,
                'remediation': 'Update TLS configuration to use only TLS 1.2 or higher with secure cipher suites.'
            },
            {
                'cve_id': 'CVE-2025-7890',
                'title': 'Default Credentials in Network Device',
                'description': 'Network device is using default or weak credentials.',
                'severity': 'high',
                'cvss_score': 8.1,
                'remediation': 'Change default credentials and implement strong password policy.'
            }
        ]
        
        # Create vulnerabilities for selected assets
        import random
        vulns_created = 0
        
        for asset in selected_assets:
            # Update last scan time
            asset.last_scan = datetime.datetime.utcnow()
            
            # Randomly select 1-3 vulnerabilities for this asset
            num_vulns = random.randint(1, 3)
            selected_vulns = random.sample(sample_vulns, min(num_vulns, len(sample_vulns)))
            
            for vuln_data in selected_vulns:
                # Check if this vulnerability already exists for this asset
                existing_vuln = Vulnerability.query.filter_by(
                    asset_id=asset.id,
                    cve_id=vuln_data['cve_id']
                ).first()
                
                if not existing_vuln:
                    vulnerability = Vulnerability(
                        asset_id=asset.id,
                        cve_id=vuln_data['cve_id'],
                        title=vuln_data['title'],
                        description=vuln_data['description'],
                        severity=vuln_data['severity'],
                        cvss_score=vuln_data['cvss_score'],
                        remediation=vuln_data['remediation'],
                        status='open'
                    )
                    db.session.add(vulnerability)
                    vulns_created += 1
        
        db.session.commit()
        
        flash(f'Scan completed. {vulns_created} new vulnerabilities found.', 'info')
        return redirect(url_for('vulnerabilities.index'))
    
    return render_template(
        'vulnerabilities/scan.html',
        title='Run Vulnerability Scan',
        form=form
    )

@vulnerabilities_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for vulnerability statistics"""
    # Get vulnerability statistics for charts
    query = Vulnerability.query.join(Asset).filter(Asset.organization_id == current_user.organization_id)
    
    # By severity
    severity_stats = {
        'critical': query.filter(Vulnerability.severity == 'critical').count(),
        'high': query.filter(Vulnerability.severity == 'high').count(),
        'medium': query.filter(Vulnerability.severity == 'medium').count(),
        'low': query.filter(Vulnerability.severity == 'low').count()
    }
    
    # By status
    status_stats = {
        'open': query.filter(Vulnerability.status == 'open').count(),
        'in_progress': query.filter(Vulnerability.status == 'in_progress').count(),
        'fixed': query.filter(Vulnerability.status == 'fixed').count(),
        'accepted_risk': query.filter(Vulnerability.status == 'accepted_risk').count(),
        'false_positive': query.filter(Vulnerability.status == 'false_positive').count()
    }
    
    # By asset (top 5)
    asset_query = db.session.query(
        Asset.name,
        db.func.count(Vulnerability.id).label('count')
    ).join(
        Vulnerability
    ).filter(
        Asset.organization_id == current_user.organization_id
    ).group_by(
        Asset.name
    ).order_by(
        db.desc('count')
    ).limit(5).all()
    
    asset_stats = {asset.name: count for asset, count in asset_query}
    
    # By time (last 30 days)
    thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    
    daily_query = db.session.query(
        db.func.date(Vulnerability.detected_at).label('date'),
        db.func.count().label('count')
    ).join(
        Asset
    ).filter(
        Asset.organization_id == current_user.organization_id,
        Vulnerability.detected_at >= thirty_days_ago
    ).group_by(
        db.func.date(Vulnerability.detected_at)
    ).order_by(
        db.func.date(Vulnerability.detected_at)
    ).all()
    
    daily_stats = {str(date): count for date, count in daily_query}
    
    return jsonify({
        'severity': severity_stats,
        'status': status_stats,
        'assets': asset_stats,
        'daily': daily_stats
    })

