from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DateField, MultipleFileField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError, Regexp
from app.models.user import User
import re

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=64),
        Regexp('^[A-Za-z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    company = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        """Validate email is not already registered"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email or sign in.')
    
    def validate_username(self, username):
        """Validate username is not already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please use a different username.')
    
    def validate_password(self, password):
        """Validate password meets complexity requirements"""
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password.data):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[^A-Za-z0-9]', password.data):
            raise ValidationError('Password must contain at least one special character.')

class ResetPasswordRequestForm(FlaskForm):
    """Form for requesting password reset"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Form for resetting password"""
    password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
    
    def validate_password(self, password):
        """Validate password meets complexity requirements"""
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password.data):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[^A-Za-z0-9]', password.data):
            raise ValidationError('Password must contain at least one special character.')

class ProfileForm(FlaskForm):
    """Form for updating user profile"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=64),
        Regexp('^[A-Za-z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Profile')

class ContactForm(FlaskForm):
    """Form for contact page"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class DemoRequestForm(FlaskForm):
    """Form for requesting a demo"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    message = TextAreaField('Additional Information', validators=[Optional()])
    submit = SubmitField('Request Demo')

class OrganizationSettingsForm(FlaskForm):
    """Form for organization settings"""
    name = StringField('Organization Name', validators=[DataRequired(), Length(max=100)])
    domain = StringField('Domain', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Settings')

class UserInviteForm(FlaskForm):
    """Form for inviting users"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    submit = SubmitField('Send Invitation')

class AssetForm(FlaskForm):
    """Form for adding/editing assets"""
    name = StringField('Asset Name', validators=[DataRequired(), Length(max=100)])
    asset_type = SelectField('Asset Type', choices=[
        ('endpoint', 'Endpoint'),
        ('server', 'Server'),
        ('cloud', 'Cloud Resource'),
        ('network', 'Network Device'),
        ('application', 'Application')
    ])
    ip_address = StringField('IP Address', validators=[Optional(), Length(max=45)])
    hostname = StringField('Hostname', validators=[Optional(), Length(max=100)])
    os_type = StringField('OS Type', validators=[Optional(), Length(max=50)])
    os_version = StringField('OS Version', validators=[Optional(), Length(max=50)])
    criticality = SelectField('Criticality', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')
    submit = SubmitField('Save Asset')

class ThreatFilterForm(FlaskForm):
    """Form for filtering threats"""
    severity = SelectField('Severity', choices=[
        ('all', 'All Severities'),
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='all')
    status = SelectField('Status', choices=[
        ('all', 'All Statuses'),
        ('active', 'Active'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive')
    ], default='all')
    threat_type = SelectField('Threat Type', choices=[
        ('all', 'All Types'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('intrusion', 'Intrusion'),
        ('data_leak', 'Data Leak'),
        ('ransomware', 'Ransomware'),
        ('ddos', 'DDoS'),
        ('other', 'Other')
    ], default='all')
    source = SelectField('Source', choices=[
        ('all', 'All Sources'),
        ('endpoint', 'Endpoint'),
        ('network', 'Network'),
        ('email', 'Email'),
        ('cloud', 'Cloud'),
        ('application', 'Application'),
        ('manual', 'Manual')
    ], default='all')
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    submit = SubmitField('Apply Filters')

class ThreatActionForm(FlaskForm):
    """Form for threat actions"""
    action = SelectField('Action', choices=[
        ('contain', 'Mark as Contained'),
        ('resolve', 'Mark as Resolved'),
        ('false_positive', 'Mark as False Positive'),
        ('reactivate', 'Reactivate Threat')
    ])
    assign_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Submit')

class ThreatSimulationForm(FlaskForm):
    """Form for simulating threats"""
    name = StringField('Threat Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    threat_type = SelectField('Threat Type', choices=[
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('intrusion', 'Intrusion'),
        ('data_leak', 'Data Leak'),
        ('ransomware', 'Ransomware'),
        ('ddos', 'DDoS'),
        ('other', 'Other')
    ])
    severity = SelectField('Severity', choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ])
    source = SelectField('Source', choices=[
        ('endpoint', 'Endpoint'),
        ('network', 'Network'),
        ('email', 'Email'),
        ('cloud', 'Cloud'),
        ('application', 'Application'),
        ('manual', 'Manual')
    ])
    asset_id = SelectField('Affected Asset', coerce=int)
    submit = SubmitField('Create Simulated Threat')

class VulnerabilityFilterForm(FlaskForm):
    """Form for filtering vulnerabilities"""
    severity = SelectField('Severity', choices=[
        ('all', 'All Severities'),
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='all')
    status = SelectField('Status', choices=[
        ('all', 'All Statuses'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('accepted_risk', 'Accepted Risk'),
        ('false_positive', 'False Positive')
    ], default='all')
    asset_id = SelectField('Asset', coerce=str, validators=[Optional()])
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    submit = SubmitField('Apply Filters')

class VulnerabilityActionForm(FlaskForm):
    """Form for vulnerability actions"""
    action = SelectField('Action', choices=[
        ('start', 'Start Remediation'),
        ('fix', 'Mark as Fixed'),
        ('accept_risk', 'Accept Risk'),
        ('false_positive', 'Mark as False Positive'),
        ('reopen', 'Reopen Vulnerability')
    ])
    assign_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Submit')

class VulnerabilityScanForm(FlaskForm):
    """Form for vulnerability scanning"""
    asset_ids = SelectMultipleField('Assets to Scan', coerce=int, validators=[DataRequired()])
    scan_type = SelectField('Scan Type', choices=[
        ('full', 'Full Scan'),
        ('quick', 'Quick Scan'),
        ('targeted', 'Targeted Scan')
    ], default='full')
    submit = SubmitField('Start Scan')

class ComplianceFilterForm(FlaskForm):
    """Form for filtering compliance controls"""
    framework_id = SelectField('Framework', coerce=int)
    category = SelectField('Category', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('all', 'All Statuses'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('not_applicable', 'Not Applicable')
    ], default='all')
    submit = SubmitField('Apply Filters')

class ComplianceAssessmentForm(FlaskForm):
    """Form for compliance assessment"""
    status = SelectField('Status', choices=[
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('not_applicable', 'Not Applicable')
    ])
    evidence = TextAreaField('Evidence', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Assessment')

class ComplianceSetupForm(FlaskForm):
    """Form for setting up compliance frameworks"""
    framework_id = SelectField('Framework', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Set Up Framework')

