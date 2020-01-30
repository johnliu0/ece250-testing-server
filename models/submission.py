"""Contains details about code submission."""

from pymodm import MongoModel, fields

class Submission(MongoModel):
    created_date = fields.DateTimeField()
    num_testcases = fields.IntegerField()
    num_passed = fields.IntegerField()
    num_failed = fields.IntegerField()

    class Meta:
        connection_alias = 'ece250ts'
