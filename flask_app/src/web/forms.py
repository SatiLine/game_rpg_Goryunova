from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired(), Length(3, 80)])
    password = PasswordField("Пароль", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired(), Length(3, 80)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(6)])


class MessageForm(FlaskForm):
    message = TextAreaField("Сообщение", validators=[DataRequired(), Length(max=500)])