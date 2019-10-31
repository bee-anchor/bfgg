from marshmallow import Schema, fields, validate

class StartSchema(Schema):
    project = fields.Str(required=True)
    testClass = fields.Str(required=True)
    javaOpts = fields.Str()

class CloneSchema(Schema):
    repo = fields.Str(required=True, validate=validate.Regexp(
        regex="(git@[\w\.]+)(:(\/\/)?)([\w\.@\:\/\-~]+)(\.git)(\/)?", 
        error="This does not look like a valid git repository")
    )