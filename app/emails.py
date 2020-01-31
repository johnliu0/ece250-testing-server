import requests
from flask import current_app as flask_app
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

def send_validation_email(user):
    domain_name = flask_app.config['DOMAIN_NAME']
    mail_domain_name = flask_app.config['MAIL_DOMAIN_NAME']
    # use https for production and http for development
    verif_link_prefix = 'http' + ('' if flask_app.env == 'development' else 's') + '://'
    verif_link = f'{verif_link_prefix}{domain_name}/auth/verify/{user.validation_token}'
    mailgun_url_param = 'sandboxa8fe96c682af4667a52b6bb5e581298f.mailgun.org' if flask_app.env == 'development' else mail_domain_name

    return requests.post(
        f'https://api.mailgun.net/v3/{mailgun_url_param}/messages',
        auth=('api', flask_app.config['MAILGUN_API_KEY']),
        data={
            'from': 'Codematic <mail@codematic.dev>',
            'to': [user.email],
            'subject': 'Email Verification',
            'html': f'<p>Thanks for signing up! To activate your account, just go here: <a href="{verif_link}">{verif_link}</a>.</p>'
        })
