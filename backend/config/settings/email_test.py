"""
Email testing configuration.
Copy this to your local.py or use as reference.
"""

# For development/testing, you can use these alternatives:

# Option 1: Console backend (emails printed to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Option 2: File backend (emails saved to files)
# EMAIL_BACKEND = 'apps.organizations.email_backend.FileEmailBackend'

# Option 3: SMTP with different provider
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Option 4: Use a different email service (e.g., SendGrid, Mailgun)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
# DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
