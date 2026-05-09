from marshmallow import Schema, fields, validate


class ATSGenerateSchema(Schema):
    resume_id        = fields.Str(required=True)
    target_job_title = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    job_description  = fields.Str(required=True, validate=validate.Length(min=50))
    company          = fields.Str(load_default="")
