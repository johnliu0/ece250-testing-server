"""User model."""

from models.submission import Submission
from pymodm import MongoModel, fields

class User(MongoModel):
    email = fields.EmailField(required=True)
    password_hash = fields.CharField(required=True)
    validation_token = fields.CharField()
    submissions = fields.EmbeddedDocumentListField(Submission, blank=True, default=[])

    class Meta:
        connection_alias = 'ece250ts'
