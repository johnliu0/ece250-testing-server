from flask import current_app as flask_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_validation_email(user):
    """Sends an email containing instructions on activating a user."""
    verif_link = f'http://142.93.152.112/auth/verify/{user.validation_token}'
    message = Mail(
        from_email='142.93.152.112',
        to_emails='user.email',
        subject='Confirm ECE250 Testing Server Account',
        html_content=f'<p>Thanks for signing up! To activate your account, just go here:<a href="{verif_link}">{verif_link}</a>.</p>')
    try:
        sg = SendGridAPIClient(flask_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(f'Successfully sent validation email to {user.email}')
    except Exception as e:
        print(f'Failed to send validation email to {user.email}: {str(e)}')
