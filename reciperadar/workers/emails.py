from flask_mail import Message

from reciperadar.workers.broker import celery


@celery.task
def issue_verification_token(base_uri, email, token):
    from reciperadar import app, mail
    with app.app_context():
        message = Message(
            subject='Welcome to RecipeRadar!',
            sender='verifications@reciperadar.com',
            recipients=[email]
        )

        verify_url = f'api/emails/verify?token={token}'
        message.body = '''
Your email address has been registered for RecipeRadar!

To confirm that you want to receive service-related emails from us at this address, please click this link: {}{}
'''.format(base_uri, verify_url)  # noqa

        mail.send(message)
