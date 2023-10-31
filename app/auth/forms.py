# forms.py
import string

from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, validators, ValidationError, EmailField
from wtforms.validators import Regexp


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[validators.DataRequired(), validators.Length(max=255)])
    email = EmailField("Email", validators=[validators.DataRequired(), validators.Email()])
    phone_number = StringField("Phone Number", validators=[validators.DataRequired(),
                                                           Regexp(r'^\+380\d{9}$',
                                                                  message='Invalid Ukrainian phone number format')])

    password = PasswordField("Password", validators=[validators.DataRequired()])

    recaptcha = RecaptchaField()
    submit = SubmitField("Register now")

    def validate_password(form, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError('Пароль повинен бути не менше 8 символів')
        if not any(char.isupper() for char in password):
            raise ValidationError('Пароль повинен містити велику літеру')
        if not any(char.islower() for char in password):
            raise ValidationError('Пароль повинен містити малу літеру')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Пароль повинен містити цифру')
        if not any(char in string.punctuation for char in password):
            raise ValidationError('Пароль повинен містити символ (не літеру і не цифру)')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[validators.DataRequired()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Login")


class VerifyCodeForm(FlaskForm):
    code = StringField('Verification Code', validators=[validators.DataRequired()])
    submit = SubmitField('Verify Code')
