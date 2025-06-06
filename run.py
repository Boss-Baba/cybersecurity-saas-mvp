from app import create_app, db
from app.models.user import User, Organization, Asset, LoginAttempt
from app.models.security import (
    Threat, Vulnerability, ComplianceFramework, ComplianceControl, 
    ComplianceAssessment, SecurityEvent, PhishingSimulation, PhishingTarget
)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Add objects to Flask shell context"""
    return {
        'db': db,
        'User': User,
        'Organization': Organization,
        'Asset': Asset,
        'LoginAttempt': LoginAttempt,
        'Threat': Threat,
        'Vulnerability': Vulnerability,
        'ComplianceFramework': ComplianceFramework,
        'ComplianceControl': ComplianceControl,
        'ComplianceAssessment': ComplianceAssessment,
        'SecurityEvent': SecurityEvent,
        'PhishingSimulation': PhishingSimulation,
        'PhishingTarget': PhishingTarget
    }

@app.cli.command("init-db")
def init_db():
    """Initialize the database with sample data"""
    import datetime
    
    # Create tables
    db.create_all()
    
    # Check if data already exists
    if User.query.first() is not None:
        print("Database already contains data. Skipping initialization.")
        return
    
    # Create sample organization
    org = Organization(
        name="Demo Company",
        domain="democompany.com",
        subscription_plan="professional",
        subscription_status="active",
        subscription_expiry=datetime.datetime.utcnow() + datetime.timedelta(days=365)
    )
    db.session.add(org)
    db.session.flush()  # Get the organization ID without committing
    
    # Create admin user
    admin = User(
        email="admin@democompany.com",
        username="admin",
        password="SecurePassword123!",
        first_name="Admin",
        last_name="User",
        company="Demo Company",
        role="admin",
        organization_id=org.id,
        is_active=True,
        email_confirmed=True
    )
    db.session.add(admin)
    
    # Create regular user
    user = User(
        email="user@democompany.com",
        username="user",
        password="SecurePassword123!",
        first_name="Regular",
        last_name="User",
        company="Demo Company",
        role="user",
        organization_id=org.id,
        is_active=True,
        email_confirmed=True
    )
    db.session.add(user)
    
    # Create sample assets
    assets = [
        Asset(
            name="Web Server",
            asset_type="server",
            ip_address="192.168.1.10",
            hostname="web-server-1",
            os_type="Linux",
            os_version="Ubuntu 22.04",
            criticality="high",
            organization_id=org.id
        ),
        Asset(
            name="Database Server",
            asset_type="server",
            ip_address="192.168.1.11",
            hostname="db-server-1",
            os_type="Linux",
            os_version="Ubuntu 22.04",
            criticality="critical",
            organization_id=org.id
        ),
        Asset(
            name="CEO Laptop",
            asset_type="endpoint",
            ip_address="192.168.1.100",
            hostname="laptop-ceo",
            os_type="Windows",
            os_version="Windows 11",
            criticality="high",
            organization_id=org.id
        ),
        Asset(
            name="Marketing Workstation",
            asset_type="endpoint",
            ip_address="192.168.1.101",
            hostname="ws-marketing-1",
            os_type="macOS",
            os_version="Ventura 13.4",
            criticality="medium",
            organization_id=org.id
        ),
        Asset(
            name="Cloud Storage",
            asset_type="cloud",
            hostname="s3-storage",
            criticality="high",
            organization_id=org.id
        )
    ]
    
    for asset in assets:
        db.session.add(asset)
    
    # Create sample threats
    threats = [
        Threat(
            name="Suspicious Login Attempt",
            description="Multiple failed login attempts from unusual location",
            threat_type="intrusion",
            severity="high",
            status="active",
            source="endpoint",
            detection_method="behavior",
            organization_id=org.id,
            asset_id=3,  # CEO Laptop
            ioc_ip="203.0.113.100"
        ),
        Threat(
            name="Potential Data Exfiltration",
            description="Unusual outbound data transfer detected",
            threat_type="data_leak",
            severity="critical",
            status="contained",
            source="network",
            detection_method="anomaly",
            organization_id=org.id,
            asset_id=2,  # Database Server
            ioc_ip="198.51.100.200"
        ),
        Threat(
            name="Phishing Email",
            description="Phishing email targeting finance department",
            threat_type="phishing",
            severity="medium",
            status="active",
            source="email",
            detection_method="signature",
            organization_id=org.id,
            ioc_domain="paypal-secure-login.com"
        )
    ]
    
    for threat in threats:
        db.session.add(threat)
    
    # Create sample vulnerabilities
    vulnerabilities = [
        Vulnerability(
            cve_id="CVE-2025-1234",
            title="Remote Code Execution in Apache",
            description="A vulnerability in Apache HTTP Server allows remote attackers to execute arbitrary code.",
            severity="critical",
            cvss_score=9.8,
            status="open",
            remediation="Update to Apache 2.6.2 or later.",
            asset_id=1  # Web Server
        ),
        Vulnerability(
            cve_id="CVE-2025-5678",
            title="SQL Injection in Web Application",
            description="A SQL injection vulnerability in the web application allows attackers to access sensitive data.",
            severity="high",
            cvss_score=8.5,
            status="in_progress",
            remediation="Update input validation in login.php.",
            asset_id=1  # Web Server
        ),
        Vulnerability(
            cve_id="CVE-2025-9012",
            title="Privilege Escalation in Windows",
            description="A local privilege escalation vulnerability in Windows allows attackers to gain admin rights.",
            severity="high",
            cvss_score=7.8,
            status="open",
            remediation="Apply Microsoft Security Update KB5025217.",
            asset_id=3  # CEO Laptop
        )
    ]
    
    for vulnerability in vulnerabilities:
        db.session.add(vulnerability)
    
    # Create sample compliance frameworks
    gdpr = ComplianceFramework(
        name="GDPR",
        description="General Data Protection Regulation",
        version="2016/679"
    )
    db.session.add(gdpr)
    
    pci = ComplianceFramework(
        name="PCI DSS",
        description="Payment Card Industry Data Security Standard",
        version="4.0"
    )
    db.session.add(pci)
    
    db.session.flush()  # Get framework IDs
    
    # Create sample compliance controls
    gdpr_controls = [
        ComplianceControl(
            control_id="GDPR-1",
            name="Lawful Basis for Processing",
            description="Personal data shall be processed lawfully, fairly and in a transparent manner.",
            category="Data Processing Principles",
            framework_id=gdpr.id
        ),
        ComplianceControl(
            control_id="GDPR-2",
            name="Purpose Limitation",
            description="Personal data shall be collected for specified, explicit and legitimate purposes.",
            category="Data Processing Principles",
            framework_id=gdpr.id
        ),
        ComplianceControl(
            control_id="GDPR-3",
            name="Data Minimization",
            description="Personal data shall be adequate, relevant and limited to what is necessary.",
            category="Data Processing Principles",
            framework_id=gdpr.id
        ),
        ComplianceControl(
            control_id="GDPR-4",
            name="Right to Access",
            description="Data subjects have the right to access their personal data.",
            category="Data Subject Rights",
            framework_id=gdpr.id
        ),
        ComplianceControl(
            control_id="GDPR-5",
            name="Right to Erasure",
            description="Data subjects have the right to request erasure of their personal data.",
            category="Data Subject Rights",
            framework_id=gdpr.id
        )
    ]
    
    for control in gdpr_controls:
        db.session.add(control)
    
    pci_controls = [
        ComplianceControl(
            control_id="PCI-1",
            name="Firewall Configuration",
            description="Install and maintain a firewall configuration to protect cardholder data.",
            category="Build and Maintain a Secure Network",
            framework_id=pci.id
        ),
        ComplianceControl(
            control_id="PCI-2",
            name="System Passwords",
            description="Do not use vendor-supplied defaults for system passwords and other security parameters.",
            category="Build and Maintain a Secure Network",
            framework_id=pci.id
        ),
        ComplianceControl(
            control_id="PCI-3",
            name="Protect Stored Data",
            description="Protect stored cardholder data.",
            category="Protect Cardholder Data",
            framework_id=pci.id
        ),
        ComplianceControl(
            control_id="PCI-4",
            name="Encrypt Transmission",
            description="Encrypt transmission of cardholder data across open, public networks.",
            category="Protect Cardholder Data",
            framework_id=pci.id
        ),
        ComplianceControl(
            control_id="PCI-5",
            name="Anti-Virus",
            description="Use and regularly update anti-virus software or programs.",
            category="Maintain a Vulnerability Management Program",
            framework_id=pci.id
        )
    ]
    
    for control in pci_controls:
        db.session.add(control)
    
    db.session.flush()  # Get control IDs
    
    # Create sample compliance assessments
    for control in gdpr_controls:
        assessment = ComplianceAssessment(
            organization_id=org.id,
            control_id=control.id,
            status="compliant" if control.control_id in ["GDPR-1", "GDPR-2", "GDPR-4"] else "non_compliant",
            evidence="Policy document reference: POL-2025-001" if control.control_id in ["GDPR-1", "GDPR-2", "GDPR-4"] else "",
            notes="Annual review scheduled for Q3 2025",
            assessed_by=admin.id
        )
        db.session.add(assessment)
    
    for control in pci_controls:
        assessment = ComplianceAssessment(
            organization_id=org.id,
            control_id=control.id,
            status="compliant" if control.control_id in ["PCI-1", "PCI-2", "PCI-5"] else "partially_compliant",
            evidence="Firewall configuration reviewed on 2025-05-15" if control.control_id == "PCI-1" else "",
            notes="Quarterly review scheduled",
            assessed_by=admin.id
        )
        db.session.add(assessment)
    
    # Create sample security events
    events = [
        SecurityEvent(
            event_type="authentication",
            source="web_application",
            severity="medium",
            description="Failed login attempt",
            source_ip="203.0.113.100",
            username="admin@democompany.com",
            action="login",
            status="failure",
            organization_id=org.id,
            asset_id=1  # Web Server
        ),
        SecurityEvent(
            event_type="network",
            source="firewall",
            severity="high",
            description="Connection attempt to known malicious IP",
            source_ip="192.168.1.101",
            destination_ip="198.51.100.200",
            action="block",
            status="blocked",
            organization_id=org.id,
            asset_id=4  # Marketing Workstation
        ),
        SecurityEvent(
            event_type="system",
            source="endpoint",
            severity="info",
            description="System update installed",
            username="system",
            action="update",
            status="success",
            organization_id=org.id,
            asset_id=3  # CEO Laptop
        )
    ]
    
    for event in events:
        db.session.add(event)
    
    # Commit all changes
    db.session.commit()
    
    print("Database initialized with sample data.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

