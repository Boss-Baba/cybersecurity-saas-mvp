from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Organization
from app.models.security import ComplianceFramework, ComplianceControl, ComplianceAssessment
from app.utils.forms import ComplianceFilterForm, ComplianceAssessmentForm
from app.utils.decorators import admin_required
from sqlalchemy import desc
import datetime

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/')
@login_required
def index():
    """Compliance dashboard route"""
    # Get available frameworks
    frameworks = ComplianceFramework.query.all()
    
    # Get selected framework (default to first one)
    framework_id = request.args.get('framework_id', type=int)
    if not framework_id and frameworks:
        framework_id = frameworks[0].id
    
    selected_framework = ComplianceFramework.query.get(framework_id) if framework_id else None
    
    # Get compliance assessments for the organization and framework
    if selected_framework:
        assessments = ComplianceAssessment.query.filter_by(
            organization_id=current_user.organization_id
        ).join(
            ComplianceControl
        ).filter(
            ComplianceControl.framework_id == selected_framework.id
        ).all()
        
        # Group controls by category
        controls_by_category = {}
        for assessment in assessments:
            category = assessment.control.category
            if category not in controls_by_category:
                controls_by_category[category] = []
            controls_by_category[category].append({
                'assessment': assessment,
                'control': assessment.control
            })
        
        # Calculate compliance statistics
        total_controls = len(assessments)
        compliant_controls = sum(1 for a in assessments if a.status == 'compliant')
        non_compliant_controls = sum(1 for a in assessments if a.status == 'non_compliant')
        partially_compliant_controls = sum(1 for a in assessments if a.status == 'partially_compliant')
        not_applicable_controls = sum(1 for a in assessments if a.status == 'not_applicable')
        
        compliance_percentage = (compliant_controls / (total_controls - not_applicable_controls) * 100) if (total_controls - not_applicable_controls) > 0 else 0
    else:
        controls_by_category = {}
        total_controls = 0
        compliant_controls = 0
        non_compliant_controls = 0
        partially_compliant_controls = 0
        not_applicable_controls = 0
        compliance_percentage = 0
    
    return render_template(
        'compliance/index.html',
        title='Compliance Management',
        frameworks=frameworks,
        selected_framework=selected_framework,
        controls_by_category=controls_by_category,
        total_controls=total_controls,
        compliant_controls=compliant_controls,
        non_compliant_controls=non_compliant_controls,
        partially_compliant_controls=partially_compliant_controls,
        not_applicable_controls=not_applicable_controls,
        compliance_percentage=round(compliance_percentage)
    )

@compliance_bp.route('/control/<int:control_id>')
@login_required
def control(control_id):
    """View compliance control details route"""
    control = ComplianceControl.query.get_or_404(control_id)
    
    # Get assessment for this organization and control
    assessment = ComplianceAssessment.query.filter_by(
        organization_id=current_user.organization_id,
        control_id=control_id
    ).first()
    
    # If no assessment exists, create a default one
    if not assessment:
        assessment = ComplianceAssessment(
            organization_id=current_user.organization_id,
            control_id=control_id,
            status='non_compliant',
            assessed_by=current_user.id
        )
        db.session.add(assessment)
        db.session.commit()
    
    form = ComplianceAssessmentForm(obj=assessment)
    
    return render_template(
        'compliance/control.html',
        title=f'Control: {control.control_id}',
        control=control,
        assessment=assessment,
        form=form
    )

@compliance_bp.route('/control/<int:control_id>/update', methods=['POST'])
@login_required
def update_assessment(control_id):
    """Update compliance assessment route"""
    assessment = ComplianceAssessment.query.filter_by(
        organization_id=current_user.organization_id,
        control_id=control_id
    ).first_or_404()
    
    form = ComplianceAssessmentForm()
    if form.validate_on_submit():
        assessment.status = form.status.data
        assessment.evidence = form.evidence.data
        assessment.notes = form.notes.data
        assessment.assessed_by = current_user.id
        assessment.assessed_at = datetime.datetime.utcnow()
        
        db.session.commit()
        flash('Compliance assessment has been updated.', 'success')
    
    return redirect(url_for('compliance.control', control_id=control_id))

@compliance_bp.route('/report')
@login_required
def report():
    """Generate compliance report route"""
    # Get available frameworks
    frameworks = ComplianceFramework.query.all()
    
    # Get selected framework (default to first one)
    framework_id = request.args.get('framework_id', type=int)
    if not framework_id and frameworks:
        framework_id = frameworks[0].id
    
    selected_framework = ComplianceFramework.query.get(framework_id) if framework_id else None
    
    if selected_framework:
        # Get compliance assessments for the organization and framework
        assessments = ComplianceAssessment.query.filter_by(
            organization_id=current_user.organization_id
        ).join(
            ComplianceControl
        ).filter(
            ComplianceControl.framework_id == selected_framework.id
        ).all()
        
        # Calculate compliance statistics
        total_controls = len(assessments)
        compliant_controls = sum(1 for a in assessments if a.status == 'compliant')
        non_compliant_controls = sum(1 for a in assessments if a.status == 'non_compliant')
        partially_compliant_controls = sum(1 for a in assessments if a.status == 'partially_compliant')
        not_applicable_controls = sum(1 for a in assessments if a.status == 'not_applicable')
        
        applicable_controls = total_controls - not_applicable_controls
        compliance_percentage = (compliant_controls / applicable_controls * 100) if applicable_controls > 0 else 0
        
        # Group controls by category
        controls_by_category = {}
        for assessment in assessments:
            category = assessment.control.category
            if category not in controls_by_category:
                controls_by_category[category] = []
            controls_by_category[category].append({
                'assessment': assessment,
                'control': assessment.control
            })
        
        # Get organization info
        organization = Organization.query.get(current_user.organization_id)
        
        return render_template(
            'compliance/report.html',
            title=f'{selected_framework.name} Compliance Report',
            framework=selected_framework,
            organization=organization,
            controls_by_category=controls_by_category,
            total_controls=total_controls,
            compliant_controls=compliant_controls,
            non_compliant_controls=non_compliant_controls,
            partially_compliant_controls=partially_compliant_controls,
            not_applicable_controls=not_applicable_controls,
            compliance_percentage=round(compliance_percentage),
            report_date=datetime.datetime.utcnow()
        )
    else:
        flash('Please select a compliance framework.', 'warning')
        return redirect(url_for('compliance.index'))

@compliance_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for compliance statistics"""
    # Get available frameworks
    frameworks = ComplianceFramework.query.all()
    
    framework_stats = {}
    for framework in frameworks:
        # Get compliance assessments for the organization and framework
        assessments = ComplianceAssessment.query.filter_by(
            organization_id=current_user.organization_id
        ).join(
            ComplianceControl
        ).filter(
            ComplianceControl.framework_id == framework.id
        ).all()
        
        # Calculate compliance statistics
        total_controls = len(assessments)
        compliant_controls = sum(1 for a in assessments if a.status == 'compliant')
        non_compliant_controls = sum(1 for a in assessments if a.status == 'non_compliant')
        partially_compliant_controls = sum(1 for a in assessments if a.status == 'partially_compliant')
        not_applicable_controls = sum(1 for a in assessments if a.status == 'not_applicable')
        
        applicable_controls = total_controls - not_applicable_controls
        compliance_percentage = (compliant_controls / applicable_controls * 100) if applicable_controls > 0 else 0
        
        framework_stats[framework.name] = {
            'total': total_controls,
            'compliant': compliant_controls,
            'non_compliant': non_compliant_controls,
            'partially_compliant': partially_compliant_controls,
            'not_applicable': not_applicable_controls,
            'percentage': round(compliance_percentage)
        }
    
    return jsonify(framework_stats)

@compliance_bp.route('/setup', methods=['GET', 'POST'])
@login_required
@admin_required
def setup():
    """Setup compliance frameworks route (admin only)"""
    from app.utils.forms import ComplianceSetupForm
    
    form = ComplianceSetupForm()
    
    # Get available frameworks
    available_frameworks = ComplianceFramework.query.all()
    form.framework_id.choices = [(f.id, f.name) for f in available_frameworks]
    
    if form.validate_on_submit():
        framework = ComplianceFramework.query.get(form.framework_id.data)
        
        # Check if assessments already exist
        existing_assessments = ComplianceAssessment.query.filter_by(
            organization_id=current_user.organization_id
        ).join(
            ComplianceControl
        ).filter(
            ComplianceControl.framework_id == framework.id
        ).count()
        
        if existing_assessments > 0:
            flash(f'Assessments for {framework.name} already exist.', 'warning')
        else:
            # Create initial assessments for all controls in the framework
            controls = ComplianceControl.query.filter_by(framework_id=framework.id).all()
            
            for control in controls:
                assessment = ComplianceAssessment(
                    organization_id=current_user.organization_id,
                    control_id=control.id,
                    status='non_compliant',
                    assessed_by=current_user.id
                )
                db.session.add(assessment)
            
            db.session.commit()
            flash(f'{framework.name} has been set up for your organization.', 'success')
        
        return redirect(url_for('compliance.index', framework_id=framework.id))
    
    return render_template(
        'compliance/setup.html',
        title='Setup Compliance Framework',
        form=form
    )

