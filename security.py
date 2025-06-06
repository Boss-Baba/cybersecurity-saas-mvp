from app import db
from datetime import datetime
import uuid

class Threat(db.Model):
    """Model for security threats detected in the system"""
    __tablename__ = 'threats'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    threat_type = db.Column(db.String(50), nullable=False)  # 'malware', 'phishing', 'intrusion', 'data_leak', etc.
    severity = db.Column(db.String(20), nullable=False)  # 'critical', 'high', 'medium', 'low'
    status = db.Column(db.String(20), default='active')  # 'active', 'contained', 'resolved', 'false_positive'
    source = db.Column(db.String(50), nullable=True)  # 'endpoint', 'network', 'email', 'cloud', etc.
    detection_method = db.Column(db.String(50), nullable=True)  # 'signature', 'behavior', 'anomaly', 'ai', 'manual'
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization')
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    asset = db.relationship('Asset')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assignee = db.relationship('User')
    
    # Indicators of compromise
    ioc_hash = db.Column(db.String(64), nullable=True)
    ioc_ip = db.Column(db.String(45), nullable=True)
    ioc_domain = db.Column(db.String(255), nullable=True)
    ioc_url = db.Column(db.String(2048), nullable=True)
    
    def __repr__(self):
        return f'<Threat {self.name}>'


class Vulnerability(db.Model):
    """Model for vulnerabilities detected in assets"""
    __tablename__ = 'vulnerabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    cve_id = db.Column(db.String(20), nullable=True)  # CVE identifier if available
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=False)  # 'critical', 'high', 'medium', 'low'
    cvss_score = db.Column(db.Float, nullable=True)  # CVSS score if available
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'fixed', 'accepted_risk', 'false_positive'
    remediation = db.Column(db.Text, nullable=True)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    fixed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    asset = db.relationship('Asset', back_populates='vulnerabilities')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assignee = db.relationship('User')
    
    def __repr__(self):
        return f'<Vulnerability {self.title}>'


class ComplianceFramework(db.Model):
    """Model for compliance frameworks"""
    __tablename__ = 'compliance_frameworks'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    controls = db.relationship('ComplianceControl', back_populates='framework')
    
    def __repr__(self):
        return f'<ComplianceFramework {self.name}>'


class ComplianceControl(db.Model):
    """Model for compliance controls within frameworks"""
    __tablename__ = 'compliance_controls'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    control_id = db.Column(db.String(50), nullable=False)  # e.g., 'AC-1', 'ID.AM-1'
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    framework_id = db.Column(db.Integer, db.ForeignKey('compliance_frameworks.id'))
    framework = db.relationship('ComplianceFramework', back_populates='controls')
    assessments = db.relationship('ComplianceAssessment', back_populates='control')
    
    def __repr__(self):
        return f'<ComplianceControl {self.control_id}>'


class ComplianceAssessment(db.Model):
    """Model for compliance assessments for organizations"""
    __tablename__ = 'compliance_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(20), nullable=False)  # 'compliant', 'non_compliant', 'partially_compliant', 'not_applicable'
    evidence = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization')
    control_id = db.Column(db.Integer, db.ForeignKey('compliance_controls.id'))
    control = db.relationship('ComplianceControl', back_populates='assessments')
    assessed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assessor = db.relationship('User')
    
    def __repr__(self):
        return f'<ComplianceAssessment {self.control_id} {self.status}>'


class SecurityEvent(db.Model):
    """Model for security events and logs"""
    __tablename__ = 'security_events'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    event_type = db.Column(db.String(50), nullable=False)  # 'authentication', 'access', 'network', 'system', etc.
    source = db.Column(db.String(50), nullable=True)  # 'firewall', 'endpoint', 'server', 'application', etc.
    severity = db.Column(db.String(20), nullable=False)  # 'critical', 'high', 'medium', 'low', 'info'
    description = db.Column(db.Text, nullable=True)
    raw_data = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization')
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    asset = db.relationship('Asset')
    
    # Event details
    source_ip = db.Column(db.String(45), nullable=True)
    destination_ip = db.Column(db.String(45), nullable=True)
    username = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=True)  # 'success', 'failure', 'blocked', etc.
    
    def __repr__(self):
        return f'<SecurityEvent {self.event_type} {self.severity}>'


class PhishingSimulation(db.Model):
    """Model for phishing simulation campaigns"""
    __tablename__ = 'phishing_simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    template = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'scheduled', 'in_progress', 'completed', 'cancelled'
    scheduled_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('User')
    targets = db.relationship('PhishingTarget', back_populates='simulation')
    
    # Statistics
    total_targets = db.Column(db.Integer, default=0)
    emails_sent = db.Column(db.Integer, default=0)
    emails_opened = db.Column(db.Integer, default=0)
    links_clicked = db.Column(db.Integer, default=0)
    data_entered = db.Column(db.Integer, default=0)
    reported = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<PhishingSimulation {self.name}>'


class PhishingTarget(db.Model):
    """Model for targets in phishing simulations"""
    __tablename__ = 'phishing_targets'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'sent', 'opened', 'clicked', 'entered_data', 'reported'
    sent_at = db.Column(db.DateTime, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    data_entered_at = db.Column(db.DateTime, nullable=True)
    reported_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    simulation_id = db.Column(db.Integer, db.ForeignKey('phishing_simulations.id'))
    simulation = db.relationship('PhishingSimulation', back_populates='targets')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<PhishingTarget {self.email}>'

