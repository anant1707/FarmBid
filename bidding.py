from flask import Flask,render_template,request,redirect,url_for,flash,session
import psycopg2 as psql
from forms import ResetForm, RegistrationForm,LoginForm,EmptyForm,UpdateForm,ForgotForm,NewPassForm,ImgForm,ChangePassword
import os
from passlib.hash import pbkdf2_sha256
import sms
import random
from datetime import date
import pickle
import numpy as np

sc_X = pickle.load(open('model/sc_x.sav', 'rb'))
sc_y = pickle.load(open('model/sc_y.sav', 'rb'))
lab1 = pickle.load(open('model/labenc.pkl', 'rb'))
lab2 = pickle.load(open('model/labenc1.pkl', 'rb'))
enco = pickle.load(open('model/onehot.pkl', 'rb'))
model =pickle.load(open('model/finalmodel.sav', 'rb'))

def pred(X):
    X[:,1]=lab1.transform(X[:,1])
    X[:,2] =lab2.transform(X[:,2])
    X=enco.transform(X).toarray()
    X=np.delete(X,26,axis=1)
    X=np.delete(X,0,axis=1)
    X=sc_X.transform(X)
    Y=model.predict(X)
    Y=sc_y.inverse_transform(Y)
    return Y

PEOPLE_FOLDER=os.path.join('static','media/profile_image')
#conn=psql.connect("dbname='PROJECT' user='postgres' host='localhost' password='1234'")
conn=psql.connect("dbname='PROJECT' user='postgres' host='localhost' password='Anant@1707'")
app=Flask(__name__)
app.secret_key='Nottobetold'
app.config['UPLOAD_FOLDER']=PEOPLE_FOLDER

def dataret(email):
    cursor=conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='userinfo'")
    list1 = [a[0] for a in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM userinfo where email='{email}'")
    dict1 = dict(zip(tuple(list1), cursor.fetchone()))
    return dict1

@app.route('/')
def home():
    print(pred(np.array([2019, 'Paddy', 'Punjab']).reshape(1, -1)))
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if request.method=='POST':
        if form.is_submitted():
            cursor=conn.cursor()
            result=request.form.to_dict()
            result['email']=form.data['email'].lower()
            form.image.data.save(os.path.join(os.getcwd(),'static/media/profile_image',form.data['email'].lower()))
            regdata=[]
            for key,value in result.items():
                if(key=='submit' or key=='cpassword' or key=='csrf_token'):
                    continue
                elif (key=='password'):
                    regdata.append(pbkdf2_sha256.hash(value))
                elif(key!='type'):
                    regdata.append(value)
                else:
                    if(value=='1'):
                        regdata.append(f"F-{result['aadhar']}")
                    else:
                        regdata.append(f"B-{result['aadhar']}")
            try:
                cursor.execute(f"INSERT INTO USERINFO VALUES {tuple(regdata)}")
            except:
                flash(f"User Already exists","danger")
                return redirect(url_for('login'))
            else:
                conn.commit()
                cursor.close()
                flash("Registration Successful!","success")
                return redirect(url_for('login'))
        else:
            return render_template('register.html',form=form)
    else:
        return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if(request.method == 'POST'):
        cursor=conn.cursor()
        result=form.data
        cursor.execute(f"Select passwordd from userinfo where lower(email)='{result['email'].lower()}'")
        a=cursor.fetchone()
        if a is None:
            flash(f"NO ACCOUNT EXISTS WITH THIS USERNAME",'danger')
            return redirect(url_for('register'))
        else:
            dict1 = dataret(result['email'].lower())
            if pbkdf2_sha256.verify(result['password'], a[0]):
                session['email']=result['email'].lower()
                session['logged-in']=True
                session['phone']=dict1['phone']
                full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
                session['image']=full_filename
                return redirect(url_for('profile'))

            else:
                flash("Incorrect Password!","danger")
                return render_template("login.html",form=form)
    else:
        flash("welcome to login page!", "success")
        return render_template('login.html',form=form)

@app.route('/profile',methods=['GET','POST'])
def profile():
    form=EmptyForm()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
    return render_template('profile.html',dp=full_filename,form=form, dict1=dataret(session['email']))

@app.route('/updateprofile',methods=['GET','POST'])
def updateprofile():
    cursor=conn.cursor()
    form=UpdateForm()
    email=session['email']
    dict1=dataret(email)
    if form.is_submitted():
        cursor.execute(f"UPDATE USERINFO set first_name='{form.first_name.data}',last_name='{form.last_name.data}',dob='{form.dob.data}',pincode={form.pincode.data},address='{form.address.data}' where email='{email}'")
        conn.commit()
        cursor.close()
        flash("Update Successfull!", "success")
        return redirect('profile')
    else:
        form.first_name.data=dict1['first_name']
        form.last_name.data = dict1['last_name']
        form.pincode.data=dict1['pincode']
        form.dob.data=dict1['dob']
        form.address.data=dict1['address']

        return render_template('updateprofile.html',form=form,dict1=dict1)

@app.route('/updateimg', methods=['GET', 'POST'])
def updateimg():
    form=ImgForm()
    if request.method == 'POST':
        if form.is_submitted():
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], session['email']))
            form.image.data.save(os.path.join(os.getcwd(), 'static/media/profile_image', session['email']))
            return redirect(url_for('profile'))

    else:
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
        return render_template('updateimg.html',form=form,dp=full_filename)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form=ForgotForm()
    cur = conn.cursor()
    if request.method == 'POST':
        phone=form.data['phone']
        cur.execute(f"select email from userinfo where phone = '{phone}' ")

        a=cur.fetchone()
        if(a == None):
            flash("You are not registered!!,REGISTER NOW", 'danger')
            return redirect(url_for('register'))
        else:
            session['email'] = a[0]
            session['phone'] = phone
            session['logged-in']=False
            return redirect(url_for('resetpass'))

    return render_template('forgot.html',form=form)

@app.route('/reset', methods=['GET', 'POST'])
def resetpass():
    cur = conn.cursor()
    form= ResetForm()
    if request.method == 'POST':
        ootp = form.data['otp']
        if ootp == session['otp']:

            return redirect(url_for('newpass'))
        else:

            flash('INVALID OTP', 'danger')
            return redirect(url_for('resetpass'))


    otp1 = str(random.randrange(100000, 999999))
    print(otp1)
    URL = 'https://www.way2sms.com/api/v1/sendCampaign'
    session['otp']=otp1
    phone=session['phone']

    # resp=sms.sendPostRequest(URL, 'C23FTIDPYUYZVP7UV238S0QC1POBFWMR', 'N1AY9Q2S52NHUADE', 'stage', phone, '9781396442', f"Your OTP (One Time Password) to change your password is: {otp1} Do not share this with anyone!   Team college+")
    #print(resp.text)
    return render_template('verifyotp.html',form=form)

@app.route('/changepass',methods=['GET','POST'])
def changepass():
    form=ChangePassword()
    if request.method=='POST':
        if form.is_submitted():
            oldp=form.oldpassword.data
            dict1=dataret(session['email'])
            if pbkdf2_sha256.verify(oldp,dict1['passwordd']):
                cursor=conn.cursor()
                newpassworda=pbkdf2_sha256.hash(form.password.data)
                cursor.execute(f" UPDATE  userinfo  set passwordd = '{newpassworda}' where email='{session['email']}' ")
                conn.commit()
                flash('Update successfull', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Enter Correct old password', 'danger')
                return redirect(url_for('changepass'))

    return render_template('newpass.html',form=form,title="Change Password")


@app.route('/newpass', methods=['GET', 'POST'])
def newpass():
    form=NewPassForm()
    cur = conn.cursor()
    if request.method == 'POST':
        newpassword = form.data['password']
        confirmnewpassword = form.data['cpassword']

        if (newpassword == confirmnewpassword):
            newpassworda = pbkdf2_sha256.hash(newpassword)

            cur.execute(
                f" UPDATE  userinfo  set passwordd = '{newpassworda}' where email =  '{session['email']}' ")
            conn.commit()
            session['logged-in']=True
            return redirect(url_for('profile'))
        else:
            flash("passwords didnt match", 'danger')
            return redirect(url_for('newpass'))
    return render_template('newpass.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    session.pop('logged-in', False)
    session.pop('phone', None)
    return redirect(url_for('login'))



if(__name__== '__main__'):
        app.run(debug=True)


