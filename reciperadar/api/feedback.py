from base58 import b58encode
from flask import jsonify, request
from urllib.request import urlopen
from uuid import uuid4

from reciperadar import app
from reciperadar.models.feedback import Feedback


@app.route('/api/feedback', methods=['POST'])
def feedback():
    issue, image_data_uri = request.json
    image = urlopen(image_data_uri)

    feedback_id = b58encode(uuid4().bytes).decode('utf-8')
    feedback = Feedback(
        id=feedback_id,
        issue=issue,
        image=image.file.read()
    )
    feedback.distribute()

    return jsonify({})
