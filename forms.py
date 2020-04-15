from flask_wtf import Form
from wtforms import StringField,TextAreaField,BooleanField,IntegerField,DateField,PasswordField,SelectField,SubmitField
from wtforms.validators import DataRequired,Length,Email,EqualTo
from flask_wtf.file import FileField,FileAllowed

class RegistrationForm(Form):
   first_name = StringField("First Name",validators=[DataRequired(),Length(min=2,max=30)])
   last_name= StringField("Last Name",validators=[DataRequired(),Length(min=2,max=30)])
   phone=StringField("Phone Number",validators=[DataRequired()])
   email=StringField('Email',validators=[DataRequired(),Email()])
   password=PasswordField("Password",validators=[DataRequired(),Length(min=8,max=20)])
   cpassword = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8, max=20),EqualTo('password')])
   address = TextAreaField("Address Feild", validators=[DataRequired(), Length(max=500)])
   pincode = StringField("Pincode", validators=[DataRequired(), Length(min=6, max=6)])
   aadhar=StringField("Aadhar Number",validators=[DataRequired(),Length(min=12,max=12)])
   panno=StringField("PAN NO.",validators=[DataRequired(),Length(min=10,max=10)])
   gst=StringField("GST",validators=[DataRequired(),Length(min=10,max=10)])
   dob=StringField("DOB")
   type=SelectField(u'Type',choices=[('1','FARMER'),('2','BUYER')])
   image=FileField(validators=[FileAllowed(['jpg','png'],'images only'),DataRequired()])
   submit=SubmitField("Sign Up")

class LoginForm(Form):
   email = StringField('Email', validators=[DataRequired(), Email()])
   password=PasswordField("Password",validators=[DataRequired(),Length(min=8,max=20)])
   submit=SubmitField("Login")





