from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError


class UploadFileForm(FlaskForm):
    file = FileField('Select File', validators=[
        FileRequired(),
        FileAllowed({'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'csv'}, 'Invalid file type!')
    ])
    submit = SubmitField('Convert')


class EncryptPDFForm(FlaskForm):
    pdf = FileField('Select PDF File', validators=[
        FileRequired(),
        FileAllowed({'pdf'}, 'Only PDF files allowed!')
    ])
    password = PasswordField('Encryption Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    submit = SubmitField('Encrypt PDF')


class DecryptPDFForm(FlaskForm):
    pdf = FileField('Select Encrypted PDF', validators=[
        FileRequired(),
        FileAllowed({'pdf'}, 'Only PDF files allowed!')
    ])
    password = PasswordField('Decryption Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Decrypt PDF')


class WatermarkPDFForm(FlaskForm):
    pdf = FileField('Select PDF File', validators=[
        FileRequired(),
        FileAllowed({'pdf'}, 'Only PDF files allowed!')
    ])
    watermark_text = StringField('Watermark Text', validators=[
        DataRequired(),
        Length(min=1, max=50, message='Watermark text must be between 1 and 50 characters')
    ])
    opacity = StringField('Opacity (0.0-1.0)', default='0.2')
    submit = SubmitField('Add Watermark')


class RotatePDFForm(FlaskForm):
    pdf = FileField('Select PDF File', validators=[
        FileRequired(),
        FileAllowed({'pdf'}, 'Only PDF files allowed!')
    ])
    angle = StringField('Rotation Angle (degrees)', default='90')
    submit = SubmitField('Rotate PDF')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Import from database module
        from database import get_db_connection
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username.data,)
        ).fetchone()
        conn.close()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
