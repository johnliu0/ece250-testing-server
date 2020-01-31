import requests
from flask import current_app as flask_app
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

def send_validation_email(user):
    domain_name = flask_app.config['DOMAIN_NAME']
    verif_link = f'{domain_name}/auth/verify/{user.validation_token}'
    if flask_app.env == 'development':
        return requests.post(
    		'https://api.mailgun.net/v3/sandboxa8fe96c682af4667a52b6bb5e581298f.mailgun.org/messages',
    		auth=('api', flask_app.config['MAILGUN_API_KEY']),
    		data={
                'from': 'Excited User <mail@codematic.dev>',
    			'to': [user.email],
    			'subject': 'Hello',
    			'html': f'<p>Thanks for signing up! To activate your account, just go here: <a href="http://{verif_link}">{verif_link}</a>.</p>'})
    #else:
