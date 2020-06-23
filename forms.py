from flask_wtf import FlaskForm as Form
from wtforms import StringField,TextAreaField,PasswordField,SelectField,SubmitField,IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired,Length,Email,EqualTo
from flask_wtf.file import FileField,FileAllowed

class RegistrationForm(Form):
   first_name = StringField("First Name",validators=[InputRequired(),Length(min=2,max=30)])
   last_name= StringField("Last Name",validators=[InputRequired(),Length(min=2,max=30)])
   phone=StringField("Phone Number",validators=[InputRequired(),Length(max=10,min=10)])
   email=StringField('Email',validators=[InputRequired(),Email()])
   password=PasswordField("Password",validators=[InputRequired(),Length(min=8,max=20)])
   cpassword = PasswordField("Confirm Password", validators=[InputRequired(), Length(min=8, max=20),EqualTo('password')])
   address = TextAreaField("Address Feild", validators=[InputRequired(), Length(max=500)])
   pincode = StringField("Pincode", validators=[InputRequired(), Length(min=6, max=6)])
   aadhar=StringField("Aadhar Number",validators=[InputRequired(),Length(min=12,max=12)])
   panno=StringField("PAN NO.",validators=[InputRequired(),Length(min=10,max=10)])
   gst=StringField("GST",validators=[InputRequired(),Length(min=10,max=10)])
   dob=DateField("DOB")
   type=SelectField(u'Type',choices=[('1','FARMER'),('2','BUYER')])
   image=FileField(validators=[FileAllowed(['jpg','png','jpeg'],'images only'),InputRequired()])
   submit=SubmitField("Sign Up")

class LoginForm(Form):
   email = StringField('Email', validators=[InputRequired(), Email()])
   password=PasswordField("Password",validators=[InputRequired(),Length(min=8,max=20)])
   submit=SubmitField("Login")
class EmptyForm(Form):
   a=6


class UpdateForm(Form):
   first_name = StringField("First Name", validators=[InputRequired(), Length(min=2, max=30)])
   last_name = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=30)])
   address = TextAreaField("Address Feild", validators=[InputRequired(), Length(max=500)])
   pincode = StringField("Pincode", validators=[InputRequired(), Length(min=6, max=6)])
   submit = SubmitField("Update")

class ForgotForm(Form):
   phone = StringField("Enter Registered Phone Number", validators=[InputRequired()])
   submit = SubmitField("Request Otp")


class ResetForm(Form):
   otp = StringField("ENTER OTP", validators=[InputRequired()])
   submit = SubmitField("SUBMIT")

class NewPassForm(Form):
   password = PasswordField("Enter New Password", validators=[InputRequired(), Length(min=8, max=20)])
   cpassword = PasswordField("Confirm Password",validators=[InputRequired(), Length(min=8, max=20), EqualTo('password')])
   submit = SubmitField("UPDATE")

class ChangePassword(NewPassForm):
   oldpassword= PasswordField("Enter Existing Password", validators=[InputRequired(), Length(min=8, max=20)])
   password = PasswordField("Enter New Password", validators=[InputRequired(), Length(min=8, max=20)])
   cpassword = PasswordField("Confirm Password",validators=[InputRequired(), Length(min=8, max=20), EqualTo('password')])
   submit = SubmitField("UPDATE")


class ImgForm(Form):
   image = FileField("UPDATE IMAGE",validators=[FileAllowed(['jpg', 'png'], 'images only'), InputRequired()])
   submit = SubmitField("UPDATE IMAGE")


class CropUploadForm(Form):
   image = FileField("UPLOAD CROP IMAGE", validators=[FileAllowed(['jpg', 'png'], 'images only'),InputRequired()])
   croptype = SelectField('CROP TYPE', coerce=int)
   quantity = StringField("Quantity(in quintalls)", validators=[InputRequired(), Length(min=2, max=30)])
   description = TextAreaField("Description", validators=[InputRequired(), Length(max=100)])
   submit = SubmitField("VIEW BASE PRICE")


class AddCropForm(Form):
   image = FileField("UPLOAD CROP IMAGE", validators=[FileAllowed(['jpg', 'png'], 'images only'),InputRequired()])
   croptype = StringField("Crop Name", validators=[InputRequired(), Length(min=2, max=30)])
   state = SelectField('State', coerce=int)
   bprice= IntegerField("Set Base Price",validators=[InputRequired()])
   quantity=StringField("Quantity(in quintalls)", validators=[InputRequired(), Length(min=2, max=30)])
   description=TextAreaField("Description", validators=[InputRequired(), Length(max=100)])
   submit = SubmitField("Add Crop")

class basepriceForm(Form):
   bp=StringField("Current Price",render_kw={'readonly': True}, validators=[InputRequired()])
   Bp= StringField("New price", validators=[InputRequired()])
   submit= SubmitField("Set Base Price ")

class SearchForm(Form):
   croptype = SelectField('CROP TYPE', coerce=int)
   state= SelectField('STATE', coerce=int)
   sortby=SelectField('SORT BY',choices=[(1,'NA'),(2,'DISTANCE'),(3,'PRICE-LOW TO HIGH'),(4,'PRICE-HIGH TO LOW'),(5,'LATEST'),(6,'POPULARITY')])
   quantity=StringField("QUANTITY",validators=[InputRequired()])
   submit = SubmitField("VIEW RESULTS")

class ViewCropForm(Form):
   price=quantity=StringField("BID PRICE",validators=[InputRequired()])
   quantity = StringField("QUANTITY", validators=[InputRequired()])
   submit = SubmitField("BID NOW")

class AcceptBidForm(Form):
   Holder=StringField("Enter Holder Name", validators=[InputRequired()])
   Account=StringField("Enter Account Number", validators=[InputRequired()])
   ifsc=StringField("Enter Ifsc Code", validators=[InputRequired()])
   Transportation=StringField("Enter Transportation Details")
   Cost=IntegerField("Transportation Cost")
   Submit=SubmitField("Share details")


class payment(Form):
   paymentno=StringField("Enter Payment no", validators=[InputRequired()])
   si=StringField("Any Special Instructions?")
   Submit=SubmitField("Share Payment Details")