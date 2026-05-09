from marshmallow import Schema, fields, validate


class EducationSchema(Schema):
    degree      = fields.Str(allow_none=True)
    field       = fields.Str(allow_none=True)
    institution = fields.Str(allow_none=True)
    startYear   = fields.Str(allow_none=True)
    endYear     = fields.Str(allow_none=True)
    grade       = fields.Str(allow_none=True)


class ExperienceSchema(Schema):
    title       = fields.Str(allow_none=True)
    company     = fields.Str(allow_none=True)
    start       = fields.Str(allow_none=True)
    end         = fields.Str(allow_none=True)
    current     = fields.Bool(load_default=False)
    description = fields.Str(allow_none=True)


class CertificationSchema(Schema):
    name   = fields.Str()
    issuer = fields.Str(allow_none=True)
    year   = fields.Str(allow_none=True)


class ProjectSchema(Schema):
    name        = fields.Str()
    description = fields.Str(allow_none=True)
    stack       = fields.Str(allow_none=True)
    link        = fields.Str(allow_none=True)


class ProfileUpdateSchema(Schema):
    name                 = fields.Str(validate=validate.Length(max=120))
    phone                = fields.Str(validate=validate.Length(max=30))
    city                 = fields.Str(validate=validate.Length(max=100))
    state                = fields.Str(validate=validate.Length(max=100))
    country              = fields.Str(validate=validate.Length(max=100))
    linkedin             = fields.Str(validate=validate.Length(max=255))
    github               = fields.Str(validate=validate.Length(max=255))
    summary              = fields.Str()
    skills               = fields.List(fields.Str())
    education            = fields.List(fields.Nested(EducationSchema))
    experience           = fields.List(fields.Nested(ExperienceSchema))
    certifications       = fields.List(fields.Nested(CertificationSchema))
    projects             = fields.List(fields.Nested(ProjectSchema))
    preferred_roles      = fields.List(fields.Str())
    preferred_locations  = fields.List(fields.Str())
    salary_min           = fields.Int(allow_none=True)
    salary_max           = fields.Int(allow_none=True)
