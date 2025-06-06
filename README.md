# Cybersecurity SaaS Platform MVP

A comprehensive cybersecurity SaaS platform for SMEs and Fintech companies that addresses multiple threat vectors and compliance requirements.

## Features

- **Threat Detection & Response**
  - Sophisticated Phishing Detection
  - AI-Powered Malware Analysis
  - Zero-Day Vulnerability Protection
  - Supply Chain Attack Monitoring
  - Insider Threat Detection
  - Cloud Misconfiguration Scanning
  - Ransomware Protection
  - DDoS Attack Mitigation
  - Prompt Injection Attack Prevention

- **Compliance Management**
  - Automated compliance monitoring (GDPR, ISO 27001, etc.)
  - Compliance readiness assessments
  - Policy management and enforcement

- **Security Assessment**
  - AI-driven threat detection
  - Real-time vulnerability scanning
  - Asset discovery and management
  - Risk assessment and prioritization

- **Security Awareness**
  - Phishing simulations
  - Security awareness training
  - Customizable training modules

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap, jQuery, Chart.js
- **Authentication**: Flask-Login
- **API**: RESTful API with JWT authentication
- **Security**: CSRF protection, input validation, secure headers

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cybersecurity-saas-mvp.git
   cd cybersecurity-saas-mvp
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database with sample data:
   ```
   flask init-db
   ```

5. Run the application:
   ```
   python run.py
   ```

6. Access the application at http://localhost:5000

### Default Credentials

- Admin User:
  - Email: admin@democompany.com
  - Password: SecurePassword123!

- Regular User:
  - Email: user@democompany.com
  - Password: SecurePassword123!

## Project Structure

```
cybersecurity-saas-mvp/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── controllers/
│   │   ├── auth.py
│   │   ├── compliance.py
│   │   ├── dashboard.py
│   │   ├── errors.py
│   │   ├── main.py
│   │   ├── settings.py
│   │   ├── threats.py
│   │   └── vulnerabilities.py
│   ├── models/
│   │   ├── security.py
│   │   └── user.py
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   ├── templates/
│   │   ├── auth/
│   │   ├── compliance/
│   │   ├── dashboard/
│   │   ├── email/
│   │   ├── errors/
│   │   ├── layout.html
│   │   ├── main/
│   │   ├── settings/
│   │   ├── threats/
│   │   └── vulnerabilities/
│   └── utils/
│       ├── decorators.py
│       ├── email.py
│       ├── forms.py
│       └── security.py
├── migrations/
├── run.py
├── requirements.txt
└── README.md
```

## Development

### Adding New Features

1. Create or modify models in `app/models/`
2. Update controllers in `app/controllers/`
3. Create or modify templates in `app/templates/`
4. Add routes to the appropriate blueprint

### Database Migrations

```
flask db init  # Only needed once
flask db migrate -m "Description of changes"
flask db upgrade
```

## Deployment

### Production Configuration

1. Set environment variables:
   ```
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   export SECURITY_PASSWORD_SALT=your-secure-password-salt
   export DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. Use a production WSGI server:
   ```
   gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
   ```

3. Set up a reverse proxy (Nginx, Apache) to handle HTTPS

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact support@cybersecurity-saas.com

