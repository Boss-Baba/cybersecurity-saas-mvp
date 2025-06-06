from flask import current_app, render_template
from flask_mail import Message
from threading import Thread

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        # In a real implementation, this would use Flask-Mail
        # For the MVP, we'll just print the email content
        print(f"Subject: {msg.subject}")
        print(f"To: {msg.recipients}")
        print(f"Body: {msg.body}")

def send_email(subject, recipients, text_body, html_body=None, attachments=None, sender=None):
    """Send an email"""
    app = current_app._get_current_object()
    
    # Use default sender if not specified
    if sender is None:
        sender = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@cybersecurity-saas.com')
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user_email, reset_url):
    """Send password reset email"""
    send_email(
        subject='Reset Your Password',
        recipients=[user_email],
        text_body=render_template('email/reset_password.txt', reset_url=reset_url),
        html_body=render_template('email/reset_password.html', reset_url=reset_url)
    )

def send_confirmation_email(user_email, confirm_url):
    """Send email confirmation"""
    send_email(
        subject='Confirm Your Email',
        recipients=[user_email],
        text_body=render_template('email/confirm_email.txt', confirm_url=confirm_url),
        html_body=render_template('email/confirm_email.html', confirm_url=confirm_url)
    )

def send_invitation_email(user_email, confirm_url, inviter_first_name, inviter_last_name, organization_name, temp_password):
    """Send invitation email"""
    send_email(
        subject=f'You have been invited to join {organization_name}',
        recipients=[user_email],
        text_body=render_template(
            'email/invitation.txt',
            confirm_url=confirm_url,
            inviter_first_name=inviter_first_name,
            inviter_last_name=inviter_last_name,
            organization_name=organization_name,
            temp_password=temp_password
        ),
        html_body=render_template(
            'email/invitation.html',
            confirm_url=confirm_url,
            inviter_first_name=inviter_first_name,
            inviter_last_name=inviter_last_name,
            organization_name=organization_name,
            temp_password=temp_password
        )
    )

def send_contact_email(name, email, subject, message):
    """Send contact form email"""
    send_email(
        subject=f'Contact Form: {subject}',
        recipients=[current_app.config.get('CONTACT_EMAIL', 'contact@cybersecurity-saas.com')],
        text_body=render_template(
            'email/contact.txt',
            name=name,
            email=email,
            message=message
        ),
        html_body=render_template(
            'email/contact.html',
            name=name,
            email=email,
            message=message
        )
    )

def send_demo_request_email(name, email, company, phone, message):
    """Send demo request email"""
    send_email(
        subject=f'Demo Request from {company}',
        recipients=[current_app.config.get('SALES_EMAIL', 'sales@cybersecurity-saas.com')],
        text_body=render_template(
            'email/demo_request.txt',
            name=name,
            email=email,
            company=company,
            phone=phone,
            message=message
        ),
        html_body=render_template(
            'email/demo_request.html',
            name=name,
            email=email,
            company=company,
            phone=phone,
            message=message
        )
    )

def send_alert_email(user_email, alert_type, alert_details, alert_url):
    """Send security alert email"""
    send_email(
        subject=f'Security Alert: {alert_type}',
        recipients=[user_email],
        text_body=render_template(
            'email/alert.txt',
            alert_type=alert_type,
            alert_details=alert_details,
            alert_url=alert_url
        ),
        html_body=render_template(
            'email/alert.html',
            alert_type=alert_type,
            alert_details=alert_details,
            alert_url=alert_url
        )
    )

def send_report_email(user_email, report_type, report_date, report_url):
    """Send report email"""
    send_email(
        subject=f'{report_type} Report - {report_date}',
        recipients=[user_email],
        text_body=render_template(
            'email/report.txt',
            report_type=report_type,
            report_date=report_date,
            report_url=report_url
        ),
        html_body=render_template(
            'email/report.html',
            report_type=report_type,
            report_date=report_date,
            report_url=report_url
        )
    )

