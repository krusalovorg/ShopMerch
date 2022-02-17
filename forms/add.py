from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FileField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    #category = StringField('Категория', validators=[DataRequired()])

    category = SelectField(choices=[('', ''), ("category 1", "category 1"), ("category2", "category2")])

    cost = IntegerField('Цена (без пробелов)', validators=[DataRequired()])
    #image = FileField('Картинка', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    # <p>
    #     {{form3.image.label }}<br>
    #     {{form3.image(class="form-control") }}<br>
    #     {% for error in form3.image.errors %}
    # <p content="alert alert-danger" role="alert">
    #     {{ error }}
    # </p>
    # {% endfor %}
