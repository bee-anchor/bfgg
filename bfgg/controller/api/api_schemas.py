from marshmallow import Schema, fields, validate


class StartSchema(Schema):
    project = fields.Str(required=True)
    testClass = fields.Str(required=True)
    javaOpts = fields.Str()
    group = fields.Str(required=True)


class CloneSchema(Schema):
    group = fields.Str(required=True)
    repo = fields.Str(
        required=True,
        validate=validate.Regexp(
            regex=r"(git@[\w\.]+)(:(\/\/)?)([\w\.@\:\/\-~]+)(\.git)(\/)?",
            error="This does not look like a valid git repository",
        ),
    )


class StopSchema(Schema):
    group = fields.Str(required=True)


class ResultsSchema(Schema):
    group = fields.Str(required=True)


class GroupSchema(Schema):
    group = fields.Str(required=True)
    agents = fields.List(fields.Str, required=True)
