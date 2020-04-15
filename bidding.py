from flask import Flask,render_template,request,redirect,url_for,flash,session,send_from_directory
import psycopg2 as psql
from forms import RegistrationForm,LoginForm
import os
from passlib.hash import pbkdf2_sha256


PEOPLE_FOLDER=os.path.join('static','media/profile_image')
conn=psql.connect("dbname='PROJECT' user='postgres' host='localhost' password='Anant@1707'")
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
            print("validated")
            cursor=conn.cursor()
            result=request.form.to_dict()
            form.image.data.save(os.path.join(os.getcwd(),'static/media/profile_image',form.data['email']))
            regdata=[]
            for key,value in result.items():
                if(key=='Sign Up' or key=='cpassword' or key=='csrf_token'):
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
        cursor.execute(f"Select passwordd from userinfo where email='{result['email']}'")
        a=cursor.fetchone()
        if a is None:
            flash(f"NO ACCOUNT EXISTS WITH THIS USERNAME",'danger')
            return redirect(url_for('register'))
        else:
            pbkdf2_sha256.verify(result['password'], a[0])
            session['email']=result['email']
            session['logged-in']=True
            return redirect(url_for('profile'))
    else:
        flash("welcome to login page!", "success")
        return render_template('login.html',form=form)

@app.route('/profile',methods=['GET','POST'])
def profile():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'])
    print(session['email'])
    return render_template('profile.html',dp=full_filename)


if(__name__== '__main__'):
        app.run(debug=True)
