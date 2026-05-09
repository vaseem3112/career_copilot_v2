from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    name     = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    email    = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError("Name cannot be blank")


class LoginSchema(Schema):
    email    = fields.Email(required=True)
    password = fields.Str(required=True)


class VerifyOTPSchema(Schema):
    email = fields.Email(required=True)
    otp   = fields.Str(required=True, validate=validate.Length(min=4, max=10))


class ResendOTPSchema(Schema):
    email = fields.Email(required=True)


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    email        = fields.Email(required=True)
    token        = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
