"""Contains details about code submission."""

from pymodm import MongoModel, fields

class Submission(MongoModel):
    created_date = fields.DateTimeField()
    project_name = fields.CharField()
    num_test_cases = fields.IntegerField()
    num_passed = fields.IntegerField()
    num_failed = fields.IntegerField()

    class Meta:
        connection_alias = 'ece250ts'
