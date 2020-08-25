from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, TextAreaField, SelectField, DateField, HiddenField, IntegerField, ValidationError, PasswordField
from wtforms.validators import Length, Email, InputRequired
from wtforms.fields.html5 import DateField
# from wtforms_components import PhoneNumberField

import phonenumbers

# # Form ORM
class UserForm(FlaskForm):    
        name = TextField(' Name :   ', validators=[InputRequired(),Length(max=30)] )
        user_id = TextField(' User ID :   ', validators=[InputRequired(),Length(max=30)] )
        password = TextField(' Password :   ', validators=[InputRequired(),Length(max=30)] )
        email = TextField(' Email :   ', validators=[Email(), InputRequired(), ])
        phone = TextField(' Phone :   ', validators=[InputRequired()])
        dates = TextField(' Dates : ', validators=[InputRequired()])
        submit = SubmitField('Submit')
        id = HiddenField('id')

        locations = []
        orig_email = HiddenField("Original Email")

        def validate_phone(self, phone):
                try:
                        p = phonenumbers.parse(phone.data)
                        if not phonenumbers.is_valid_number(p):
                                raise ValueError()
                except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
                        raise ValidationError('Invalid phone number')

class LoginForm(FlaskForm):    
        name = TextField(' Name :   ', validators=[InputRequired(),Length(max=20)] )
        password = PasswordField(' Password :   ', validators=[InputRequired(),Length(max=20)] )
        submit = SubmitField('Log in')  
        

# class UserForm(ModelForm):
#     class Meta:
#         model = User
#         validators = {'name': [InputRequired()], 'email': [InputRequired(), Email()], 'phone': [InputRequired()]}


