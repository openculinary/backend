from flask_mail import Message

from reciperadar.workers.broker import celery


@celery.task
def issue_verification_token(email, token):
    from reciperadar import app, mail
    with app.app_context():
        message = Message(
            subject='Welcome to RecipeRadar!',
            sender='verifications@reciperadar.com',
            recipients=[email]
        )

        base_uri = 'https://staging.reciperadar.com'
        verify_link = '{}/api/emails/verify?token={}'.format(base_uri, token)
        message.body = '''
Your email address has been registered for RecipeRadar!

To confirm that you want to receive service-related emails from us at this address, please click this link: {}
'''.format(verify_link)  # noqa

        mail.send(message)
