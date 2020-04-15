from flask import Flask,render_template,request,redirect,url_for,flash,session,send_from_directory
import psycopg2 as psql
from forms import RegistrationForm,LoginForm,EmptyForm,UpdateForm
import os
from passlib.hash import pbkdf2_sha256

PEOPLE_FOLDER=os.path.join('static','media/profile_image')
conn=psql.connect("dbname='Project' user='postgres' host='localhost' password='Anant@1707'")
app=Flask(__name__)
app.secret_key='Nottobetold'
app.config['UPLOAD_FOLDER']=PEOPLE_FOLDER

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if request.method=='POST':
        if form.validate():
            cursor=conn.cursor()
            result=request.form.to_dict()
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
        print(result)
        cursor.execute(f"Select passwordd from userinfo where lower(email)='{result['email'].lower()}'")
        a=cursor.fetchone()
        if a is None:
            flash(f"NO ACCOUNT EXISTS WITH THIS USERNAME",'danger')
            return redirect(url_for('register'))
        else:
            if pbkdf2_sha256.verify(result['password'], a[0]):

                session['email']=result['email']
                session['logged-in']=True
                return redirect(url_for('profile'))
            else:
                flash("Incorrect Password!","danger")
                return render_template("login.html",form=form)
    else:
        flash("welcome to login page!", "success")
        return render_template('login.html',form=form)

@app.route('/profile',methods=['GET','POST'])
def profile():
    cursor=conn.cursor()
    form=EmptyForm()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='userinfo'")
    list1=[a[0] for a in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM userinfo where email='{session['email']}'")
    return render_template('profile.html',dp=full_filename,form=form,dict1=dict(zip(tuple(list1),cursor.fetchone())))

@app.route('/updateprofile',methods=['GET','POST'])
def updateprofile():
    cursor=conn.cursor()
    form=UpdateForm()
    form.address.data="12345"

    form.dob.data="22/11/19"
    form.first_name.data="rahul"
    form.last_name.data="garg"
    form.pincode.data="160036"

    return render_template('updateprofile.html',form=form)

if(__name__== '__main__'):
        app.run(debug=True)
