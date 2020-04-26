from flask_wtf import Form
from wtforms import StringField,TextAreaField,PasswordField,SelectField,SubmitField,IntegerField
from wtforms.fields.html5 import DateField
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
   dob=DateField("DOB",format='%m-%d-%Y')
   type=SelectField(u'Type',choices=[('1','FARMER'),('2','BUYER')])
   image=FileField(validators=[FileAllowed(['jpg','png'],'images only'),DataRequired()])
   submit=SubmitField("Sign Up")

class LoginForm(Form):
   email = StringField('Email', validators=[DataRequired(), Email()])
   password=PasswordField("Password",validators=[DataRequired(),Length(min=8,max=20)])
   submit=SubmitField("Login")
class EmptyForm(Form):
   a=6


class UpdateForm(Form):
   first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=30)])
   last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=30)])
   address = TextAreaField("Address Feild", validators=[DataRequired(), Length(max=500)])
   pincode = StringField("Pincode", validators=[DataRequired(), Length(min=6, max=6)])
   dob = StringField("DOB")
   submit = SubmitField("Update")

class ForgotForm(Form):
   phone = StringField("Enter Registered Phone Number", validators=[DataRequired()])
   submit = SubmitField("Request Otp")


class ResetForm(Form):
   otp = StringField("ENTER OTP", validators=[DataRequired()])
   submit = SubmitField("SUBMIT")

class NewPassForm(Form):
   password = PasswordField("Enter New Password", validators=[DataRequired(), Length(min=8, max=20)])
   cpassword = PasswordField("Confirm Password",validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')])
   submit = SubmitField("UPDATE")

class ChangePassword(NewPassForm):
   oldpassword= PasswordField("Enter Existing Password", validators=[DataRequired(), Length(min=8, max=20)])
   password = PasswordField("Enter New Password", validators=[DataRequired(), Length(min=8, max=20)])
   cpassword = PasswordField("Confirm Password",validators=[DataRequired(), Length(min=8, max=20), EqualTo('password')])
   submit = SubmitField("UPDATE")


class ImgForm(Form):
   image = FileField("UPDATE IMAGE",validators=[FileAllowed(['jpg', 'png'], 'images only'), DataRequired()])
   submit = SubmitField("UPDATE IMAGE")


class CropUploadForm(Form):
   image = FileField("UPLOAD CROP IMAGE", validators=[FileAllowed(['jpg', 'png'], 'images only')])
   croptype = SelectField('CROP TYPE', coerce=int)
   submit = SubmitField("VIEW BASE PRICE")


class AddCropForm(Form):
   image = FileField("UPLOAD CROP IMAGE", validators=[FileAllowed(['jpg', 'png'], 'images only')])
   croptype = StringField("Crop Name", validators=[DataRequired(), Length(min=2, max=30)])
   state    = SelectField('State', coerce=int)
   bprice= IntegerField("Set Base Price",validators=[DataRequired()])
   submit = SubmitField("Add Crop")
