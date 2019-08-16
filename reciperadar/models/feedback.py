from flask_mail import Message
from sqlalchemy import Column, JSON, LargeBinary, String

from reciperadar.models.base import Storable


class Feedback(Storable):
    __tablename__ = 'feedback'

    id = Column(String, primary_key=True)
    issue = Column(JSON)
    image = Column(LargeBinary)

    def distribute(self):
        from reciperadar import app, mail
        with app.app_context():
            title = self.issue.pop('issue') or '(empty)'
            title = title if len(title) < 25 else f'{title[:25]}...'

            html = '<html><body><table>'
            for k, v in self.issue.items():
                html += '<tr>'
                html += f'<th>{k}</th>'
                html += f'<td>{v}</td>'
                html += '</tr>'
            html += '</table></body></html>'

            message = Message(
                subject=f'User feedback: {title}',
                sender='verifications@reciperadar.com',
                recipients=['feedback@reciperadar.com'],
                html=html
            )
            message.attach('screenshot.png', 'image/png', self.image)
            mail.send(message)
