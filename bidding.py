from builtins import str
from flask import Flask,render_template,request,redirect,url_for,flash,session
import psycopg2 as psql
import pandas as pd
import numpy as np
from forms import ResetForm,RegistrationForm,LoginForm,EmptyForm,UpdateForm,ForgotForm,NewPassForm,ImgForm,ChangePassword,CropUploadForm,AddCropForm,basepriceForm,SearchForm,ViewCropForm
import os
from flask_wtf.file import FileField,FileAllowed
from passlib.hash import pbkdf2_sha256
import sms
import random
from datetime import date
import pickle
import numpy as np
import shutil
import datetime
G = pd.read_csv('pincode.csv')
H = pd.read_excel('FINAL1.xls' )

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
CROP_FOLDER=os.path.join('static','media/cropimg')
#conn=psql.connect("dbname='PROJECT' user='postgres' host='localhost' password='Anant@1707'")
conn=psql.connect("dbname='PROJECT' user='postgres' host='localhost' password='1234'")
app=Flask(__name__)
app.secret_key='Nottobetold'
app.config['UPLOAD_FOLDER']=PEOPLE_FOLDER
app.config['CROP_IMG']=CROP_FOLDER

def dataret(email):
    cursor=conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='userinfo'")
    list1 = [a[0] for a in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM userinfo where email='{email}'")
    dict1 = dict(zip(tuple(list1), cursor.fetchone()))
    return dict1

@app.route('/')
def home():
    session.pop('logged-in', False)
    session.pop('phone', False)
    form=EmptyForm()
    return render_template('index.html',form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    session.pop('logged-in',False)
    session.pop('phone', False)
    form=RegistrationForm()
    if request.method=='POST':
        if form.is_submitted():
            cursor=conn.cursor()
            result=request.form.to_dict()
            result['email']=form.data['email'].lower()

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
                flash(f"User Credentials exists","danger")
                return redirect(url_for('login'))
            else:

                form.image.data.save( os.path.join(os.getcwd(), 'static/media/profile_image', form.data['email'].lower()))
                session['log-in']='reg'

                session['phone']=result['phone']
                flash("Verify Otp!","info")
                return redirect(url_for('resetpass'))
        else:
            return render_template('register.html',form=form)
    else:
        return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    session.pop('logged-in',False)
    session.pop('phone',False)
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
                session['list']=None
                session['state']=None
                session['up']=1


                session['username']=dict1['username']
                return redirect(url_for('profile'))

            else:
                flash("Incorrect Password!","danger")
                return render_template("login.html",form=form)
    else:

        return render_template('login.html',form=form)

@app.route('/profile',methods=['GET','POST'])
def profile():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE','danger')
        return redirect(url_for('logout'))


    session['up']=1
    form=EmptyForm()
    session.pop('value',None)
    session.pop('quantity', None)
    session.pop('crop',None)

    session.pop('stated', None)
    session.pop('crop', None)
    session.pop('quantity', None)

    if (session.get('img')):
        os.remove(os.path.join(os.getcwd(), 'static/media/temp', session['img']))
        session.pop('img', None)

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
    return render_template('profile.html',dp=full_filename,form=form, dict1=dataret(session['email']))

@app.route('/updateprofile',methods=['GET','POST'])
def updateprofile():

    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
        session['up']=0
    cursor=conn.cursor()
    form=UpdateForm()
    email=session['email']
    dict1=dataret(email)
    if form.is_submitted():
        cursor.execute(f"UPDATE USERINFO set first_name='{form.first_name.data}',last_name='{form.last_name.data}',dob='{form.dob.data}',pincode={form.pincode.data},address='{form.address.data}' where email='{email}'")
        conn.commit()
        cursor.close()
        session.pop('list',None)
        session.pop('value',None)
        session.pop('state',None)
        session.pop('mystate', None)


        flash("Update Successfull!", "success")
        return redirect('profile')
    else:
        session.pop('value', None)
        session.pop('quantity', None)
        session.pop('crop', None)

        session.pop('stated', None)
        session.pop('crop', None)
        session.pop('quantity', None)
        form.first_name.data=dict1['first_name']
        form.last_name.data = dict1['last_name']
        form.pincode.data=dict1['pincode']
        form.dob.data=dict1['dob']
        form.address.data=dict1['address']

        return render_template('updateprofile.html',form=form,dict1=dict1)

@app.route('/updateimg', methods=['GET', 'POST'])
def updateimg():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))


    session['up'] = 0
    form=ImgForm()
    if request.method == 'POST':
        if form.is_submitted():
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], session['email']))
            form.image.data.save(os.path.join(os.getcwd(), 'static/media/profile_image', session['email']))
            return redirect(url_for('profile'))

    else:
        session.pop('value', None)
        session.pop('quantity', None)
        session.pop('crop', None)

        session.pop('stated', None)
        session.pop('crop', None)
        session.pop('quantity', None)
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
        return render_template('updateimg.html',form=form,dp=full_filename)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    session.pop('logged-in', False)
    session.pop('phone', False)
    session['up'] = 0
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
            dict1=dataret(f'{a[0]}')
            session['username']=dict1['username']
            session['up']=1
            return redirect(url_for('resetpass'))

    return render_template('forgot.html',form=form)

@app.route('/reset', methods=['GET', 'POST'])
def resetpass():
    if(not session.get('phone')):
        return redirect(url_for('login'))

    session['up']=0
    form= ResetForm()
    if request.method == 'POST':
        ootp = form.data['otp']
        if ootp == session['otp']:
            if(session.get('log-in')=='reg'):

                conn.commit()
                session.pop('log-in', None)
                session.pop('phone', None)

                return redirect(url_for('login'))




            return redirect(url_for('newpass'))
        else:

            flash('INVALID OTP', 'danger')
            return redirect(url_for('resetpass'))


    otp1 = str(random.randrange(100000, 999999))
    print(otp1)
    URL = 'https://www.way2sms.com/api/v1/sendCampaign'
    session['otp']=otp1
    phone=session['phone']

    #resp=sms.sendPostRequest(URL, 'C23FTIDPYUYZVP7UV238S0QC1POBFWMR', 'N1AY9Q2S52NHUADE', 'stage', phone, '9781396442', f"Your OTP (One Time Password) to change your password is: {otp1} Do not share this with anyone!   Team college+")
    #print(resp.text)
    return render_template('verifyotp.html',form=form)

@app.route('/changepass',methods=['GET','POST'])
def changepass():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))


    session['up'] = 0
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
    session.pop('value', None)
    session.pop('quantity', None)
    session.pop('crop', None)

    session.pop('stated', None)
    session.pop('crop', None)
    session.pop('quantity', None)
    return render_template('newpass.html',form=form,title="Change Password")


@app.route('/newpass', methods=['GET', 'POST'])
def newpass():

    session['up'] = 0
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
    session.pop('username', None)

    session.pop('list', None)
    session.pop('value',None)

    session.pop('up', None)
    session.pop('quantity', None)
    session.pop('description', None)
    session.pop('fcroplist', None)
    session.pop('fstatelist', None)

    session.pop('stated', None)
    session.pop('crop',None)
    session.pop('quantity', None)
    session.pop('state', None)
    session.pop('sortby', None)
    session.pop('mystate', None)


    if(session.get('img')):
        os.remove(os.path.join(os.getcwd(), 'static/media/temp',session['img']))
        session.pop('img', None)

    return redirect(url_for('home'))


@app.route('/upload',methods=['GET','POST'])
def upload():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if(not session['username'][0]=='F'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))

    session['up'] = 0

    form = CropUploadForm()
    if request.method=='POST':
        if form.is_submitted():
            d1=dict(session['list'])
            croptype=d1[form.croptype.data]
            #session.pop('list',None)
            print(croptype)
            from datetime import date
            year_ = date.today().year
            year_=str(year_)
            state=session['state']
            state=str(state)
            state=state.title()
            #session.pop('state',None)
            X=np.array([year_,croptype,state]).reshape(1,-1)
            print(type(croptype))
            print(type(state))
            cur = conn.cursor()
            owned = str(session['username'])
            dt = datetime.date.today().isoformat()
            cur.execute(f"select cropid from cropinfo where owned='{owned}' and crop='{croptype}' and enddate>='{dt}'")
            t = cur.fetchone()
            if (t is not None):
                flash("You have already registered this crop", 'danger')
                return redirect(url_for('upload'))
            value=pred(X)
            value[0]="{:.2f}".format(round(value[0], 2))
            session['value']=(float(value[0]*1.55))
            session['value']=float("{:.2f}".format(round(session['value'], 2)))
            session['crop']=croptype
            quantity=form.data['quantity']
            quantity=int(quantity)
            session['quantity']=quantity
            print(type(value[0]))
            pth=str(random.randint(1,900000))
            form.image.data.save(os.path.join(os.getcwd(), 'static/media/temp',pth ))
            session['img']=pth
            session['description']=str(form.data['description'])
            form=EmptyForm()
            return render_template('basebid.html',value=session['value'],form=form)

    X =G
    Y=H
    session.pop('crop', None)
    session.pop('quantity', None)
    session.pop('value', None)
    if(session.get('img')):
        os.remove(os.path.join(os.getcwd(), 'static/media/temp',session['img']))
        session.pop('img', None)

    X['statename']=X['statename'].str.lower()
    Y['State']=Y['State'].str.lower()
    dict1=dataret(session['email'])
    pincode=dict1['pincode']

    state=X['statename'].where(X['pincode']==pincode).unique()
    print(state[1])
    session['state']=state[1]
    crops=Y['Crop'].where(Y['State']==state[1]).unique()
    crops=list(crops)
    crops.pop(0)
    print(crops)
    li=[]
    i=1
    if(len(crops)!=0):
        for a in crops:
           li.append((i,a))
           i+=1
    session['list']=li

    form.croptype.choices = li

    return render_template('cropupload.html',form=form)


@app.route('/addcrop',methods=['GET','POST'])
def addcrop():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if(not session['username'][0]=='F'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    session['up'] = 0
    form=AddCropForm()
    if request.method=="POST":
        if form.is_submitted():
            Y=H
            crops=Y['Crop'].where(Y['State']==session['state']).unique()
            crops=list(crops)
            crops.pop(0)
            danger=0
            print(crops)
            cro=form.data['croptype']
            cro=str(cro)
            cro=cro.lower()
            cro=cro.title()
            value=form.data['bprice']
            value=float(value)
            print(cro)
            if len(crops)!=0:
                for crop in crops:
                    if cro==crop:
                        danger=1
                        break

            print(danger)
            if(danger==1):
                flash('This Crop is already listed for your state','danger')
                return redirect(url_for('upload'))
            cur = conn.cursor()
            owned = str(session['username'])
            dt = datetime.date.today().isoformat()
            cur.execute(f"select cropid from cropinfo where owned='{owned}' and crop='{cro}' and enddate>='{dt}'")
            t = cur.fetchone()
            if (t is not None):
                flash("You have already registered this crop", 'danger')
                return redirect(url_for('upload'))
            session['crop']=cro
            session['value']=float("{:.2f}".format(round(value,2)))
            pth=str(random.randint(1,900000))
            form.image.data.save(os.path.join(os.getcwd(), 'static/media/temp',pth ))
            session['img']=pth
            session['quantity']=int(form.data['quantity'])
            session['description']=str(form.data['description'])
            flash('Crop listing successfull','success')

            return redirect(url_for('newcrop'))
    session.pop('crop', None)
    session.pop('quantity', None)
    session.pop('value', None)
    if (session.get('img')):
        os.remove(os.path.join(os.getcwd(), 'static/media/temp', session['img']))
        session.pop('img', None)

    form.state.choices=[(1,session['state'])]
    return render_template('addcrop.html',form=form)

@app.route('/changebp',methods=['GET','POST'])
def changebp():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if(not session['username'][0]=='F'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    if(not session.get('value')):
        flash('No crop specified to change price for','danger')
        return redirect(url_for('upload'))

    session['up'] = 0
    form=basepriceForm()
    if request.method=='POST':
        if form.validate_on_submit():
            op=float(form.data['bp'])
            np=float(form.data['Bp'])
            if op>=np:
                session['value']=op
                print(session['value'])
                flash('PRICE UPDATED AND CROP UP FOR BIDDING','success')
                return redirect(url_for('newcrop'))
            else:
                flash('PRICE CANT BE HIGHER THAN PREDICTED BASE PRICE','danger')

                return redirect(url_for('changebp'))

            return redirect(url_for('profile'))
    else:
        value=session['value']
        form.bp.data=value
        return render_template('changeprice.html',form=form)


@app.route('/newcrop',methods=['GET','POST'])
def newcrop():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if(not session['username'][0]=='F'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    if(not session.get('crop')):
        return redirect(url_for('fhome'))

    session['up'] = 1
    form=EmptyForm()
    cursor=conn.cursor()

    crop=session['crop']
    baseprice=session['value']
    quantity=int(session['quantity'])
    baseprice=float(baseprice)
    description=session['description']
    crop=str(crop)
    crop=crop.title()
    dat = datetime.date.today() + datetime.timedelta(days=20)
    dat=dat.isoformat()
    print(type(dat))
    state=session['state']
    state=str(state)
    state=state.lower()
    state=state.title()

    cursor.execute(f"INSERT INTO cropinfo(owned, crop, baseprice, quantity,description,enddate,state) VALUES('{session['username']}','{crop}',{baseprice},{quantity},'{description}','{dat}','{state}');")
    conn.commit()
    cursor.close()
    cursor = conn.cursor()

    us = str(session['username'])

    cursor.execute(f"select cropid from cropinfo where owned='{us}' AND crop='{crop}' AND baseprice={baseprice} ")
    a = cursor.fetchone()
    a=a[0]
    os.rename(os.path.join(os.getcwd(), 'static/media/temp',session['img']), os.path.join(os.getcwd(), 'static/media/temp',str(a)))

    shutil.copy(os.path.join(os.getcwd(), 'static/media/temp',str(a)), os.path.join(os.getcwd(), 'static/media/cropimg',str(a)))
    os.remove(os.path.join(os.getcwd(), 'static/media/temp',str(a)))
    session.pop('crop', None)
    session.pop('quantity', None)
    session.pop('value', None)
    session.pop('img', None)
    session.pop('description', None)

    return render_template('newcrop.html',form=form ,crop=crop,value=baseprice,id=a,quantity=quantity)


@app.route('/deletecrop', methods=['GET', 'POST'])
def deletecrop():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if (not session['username'][0]=='F'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    if( not request.args.get('a') ):
        return redirect(url_for('fhome'))

    if(request.args):
        id=request.args['a']
        id=int(id)
        os.remove(os.path.join(os.getcwd(), 'static/media/cropimg', str(id)))
        cursor=conn.cursor()
        owned=session['username']
        cursor.execute(f"DELETE FROM cropinfo WHERE cropid={id} and owned='{owned}';")
        conn.commit()
        cursor.close()
        return redirect(url_for('fhome'))



@app.route('/fhome',methods=['GET','POST'])
def fhome():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if(not session['username'][0]=='F'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    session.pop('crop', None)
    session.pop('quantity', None)
    session.pop('value', None)
    if (session.get('img')):
        os.remove(os.path.join(os.getcwd(), 'static/media/temp', session['img']))
        session.pop('img', None)

    form=EmptyForm()
    session['up'] = 1
    cursor=conn.cursor()
    dict1=dataret(session['email'])
    us=str(session['username'])
    dt=datetime.date.today().isoformat()
    cursor.execute(f"select cropid,crop,baseprice,quantity,description,enddate from cropinfo where owned='{us}' and enddate>='{dt}'")

    a=cursor.fetchall()
    #list of tuples
    print(a)

    i=0
    return render_template('fhome.html',form=form,b=a,dict1=dict1,i=i)
@app.route('/bhome',methods=['GET','POST'])
def bhome():
    X=H
    Y=G
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if (not session['username'][0] == 'B'):
        flash('URL NOT FOUND', 'danger')
        return redirect(url_for('profile'))



    form = SearchForm()
    if request.method == 'POST':
        if form.is_submitted():

            d1=dict(session['fstatelist'])
            d2=dict(session['fcroplist'])
            session['stated'] = str(d1[form.state.data])

            session['quantity']=form.quantity.data
            session['crop'] = str(d2[form.croptype.data])
            session['sortby']=form.sortby.data

            return redirect(url_for('bhome'))

    cursor = conn.cursor()
    dict1 = dataret(session['email'])
    if (session.get('stated')):
        import datetime
        dt = datetime.date.today()
        dt = dt.isoformat()
        state=session['stated']
        crop=session['crop']
        sortby=session['sortby']
        sortby=int(sortby)
        quantity=session['quantity']
        q= f"select cropid,crop,baseprice,quantity,description,enddate,state from cropinfo where enddate>='{dt}' and quantity>={quantity}"
        if (sortby == 1 or sortby == 5):
            if state == 'NA':
                if crop == 'NA':
                    cursor.execute(q)
                    a = cursor.fetchall()
                    a.reverse()
                else:
                    cursor.execute(q + f"and crop='{crop}'")
                    a = cursor.fetchall()
                    a.reverse()
            else:
                if crop == 'NA':
                    cursor.execute(q + f"and state='{state}'")
                    a = cursor.fetchall()
                    a.reverse()
                else:
                    cursor.execute(q + f"and crop='{crop}' and state='{state}'")
                    a=cursor.fetchall()
                    a.reverse()
        elif sortby == 2:
                if state == 'NA':
                    if crop == 'NA':
                        cursor.execute(f"""select cropid,crop,baseprice,quantity,description,enddate,state 
                from cropinfo JOIN distances di 
                ON  cropinfo.state = di.state2 
                where di.state1='{session["mystate"]}'
                order by distance asc;""")
                        a = cursor.fetchall()
                    else:
                        cursor.execute(f"""select cropid,crop,baseprice,quantity,description,enddate,state 
                from cropinfo JOIN distances di 
                ON  cropinfo.state = di.state2 
                where di.state1='{session["mystate"]}'and crop='{crop}'
                order by distance asc;""")
                        a = cursor.fetchall()
                else:
                    if crop == 'NA':
                        cursor.execute(f"""select cropid,crop,baseprice,quantity,description,enddate,state 
                from cropinfo JOIN distances di 
                ON  cropinfo.state = di.state2 
                where di.state1='{session["mystate"]}' and state='{state}'
                order by distance asc;""")
                        a = cursor.fetchall()
                    else:
                        cursor.execute(f"""select cropid,crop,baseprice,quantity,description,enddate,state 
                from cropinfo JOIN distances di 
                ON  cropinfo.state = di.state2 
                where di.state1='{session["mystate"]}'and crop='{crop}' and state='{state}'
                order by distance asc;""")

                        a = cursor.fetchall()
        elif sortby == 3:
            if state == 'NA':
                if crop == 'NA':
                    cursor.execute(q + " order by baseprice asc;")
                    a = cursor.fetchall()
                else:
                    cursor.execute(q + f"and crop='{crop}'" + " order by baseprice asc;")
                    a = cursor.fetchall()

            else:
                if crop == 'NA':
                    cursor.execute(q + f"and state='{state}'" + " order by baseprice asc;")
                    a = cursor.fetchall()
                else:
                    cursor.execute(q + f"and crop='{crop}' and state='{state}'" + "order by baseprice asc")
                    a = cursor.fetchall()

        elif sortby == 4:
            if state == 'NA':
                if crop == 'NA':
                    cursor.execute(q + " order by baseprice desc;")
                    a = cursor.fetchall()
                else:
                    cursor.execute(q + f"and crop='{crop}'" + " order by baseprice desc;")
                    a = cursor.fetchall()
            else:
                if crop == 'NA':
                    cursor.execute(q + f"and state='{state}'" + " order by baseprice desc;")
                    a = cursor.fetchall()
                else:
                    cursor.execute(q + f"and crop='{crop}' and state='{state}'" + "order by baseprice desc;")
                    a = cursor.fetchall()
        l1=(session['fcroplist'])
        l2=(session['fstatelist'])
        l1[0]=list(l1[0])
        l1[0][1]=crop
        l1[0]=tuple(l1[0])
        l2[0]=list(l2[0])
        l2[0][1] = state
        l2[0] = tuple(l2[0])
        l2[0] = tuple(l2[0])
        l1=list(l1)
        l2=list(l2)
        form.croptype.choices=l1
        form.quantity.data=int(quantity)
        form.state.choices=l2
        session['fcroplist']=l1
        session['fstatelist']=l2
        return render_template('bhome.html', form=form, b=a)




    else:
        form = SearchForm()
        session.pop('sortby', None)
        session.pop('stated', None)
        session.pop('crop', None)
        session.pop('quantity', None)
        import datetime
        dt=datetime.date.today()
        dt=dt.isoformat()


        cursor.execute(f"select cropid,crop,baseprice,quantity,description,enddate,state from cropinfo where enddate>='{dt}'")
        a = cursor.fetchall()
        Y['statename'] = Y['statename'].str.lower()
        X['State'] = X['State'].str.lower()
        dict1 = dataret(session['email'])
        pincode = dict1['pincode']
        state = Y['statename'].where(Y['pincode'] == pincode).unique()

        session['mystate'] = state[1].title()
        print(state[1].title())
        cursor.execute("select distinct crop from cropinfo")
        croplist=cursor.fetchall()
        cclist=[]
        for i in croplist:
            cclist.append(i[0])
        clist=list(X['Crop'].dropna().unique())
        clist.extend(cclist)
        croplist=list(set(clist))
        statelist=list(X['State'].dropna().unique())

        fcroplist=[]
        i=2
        fcroplist.append((1,'NA'))
        for j in croplist:
            fcroplist.append((i,j))
            i+=1
        fstatelist=[]
        i = 2
        fstatelist.append((1, 'NA'))
        for j in statelist:
            fstatelist.append((i, j.title()))
            i += 1
        form.croptype.choices = fcroplist
        form.state.choices=fstatelist
        session['fcroplist']=fcroplist
        session['fstatelist']=fstatelist
        form.quantity.data=0
        return render_template('bhome.html', form=form, b=a, dict1=dict1)

@app.route('/bhomereset')
def bhomereset():
    session.pop('sortby', None)
    session.pop('stated', None)
    session.pop('crop', None)
    session.pop('quantity', None)
    session.pop('fstatelist', None)
    session.pop('fcroplist', None)
    return redirect(url_for('bhome'))


@app.route('/viewcrop',methods=['GET','POST'])
def viewcrop():
    form=ViewCropForm()
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE', 'danger')
        return redirect(url_for('logout'))
    if (not session['username'][0]=='B'):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('profile'))
    if (not request.args.get('a')):
        flash('Nothing selected to view details of', 'danger')
        return redirect(url_for('profile'))
    if request.method=='POST':
        id=request.args.get('a')
        print(id)
        bid=form.price.data
        quantity=form.quantity.data
        byer = session['username']
        cursor = conn.cursor()
        cursor.execute(f"select baseprice,quantity from cropinfo where cropid='{id}';")
        x=cursor.fetchone()



        if float(bid)<float(x[0]):
            flash('YOUR BID CANT BE LESS THAN BASEPRICE','danger')
            return redirect(url_for('viewcrop',a=id))
        if int(quantity)> int(x[1]):
            flash('QUANTITY NOT AVAILABLE FOR THE CROP', 'danger')
            return redirect(url_for('viewcrop', a=id))
        import datetime
        dt = datetime.date.today()
        dt = dt.isoformat()

        cursor.execute(f"select bidid from bidding where cropid={id} and buyer='{byer}';")

        y = cursor.fetchone()
        if y is not None:
            buyid=y[0]
            flash("BID UPDATED",'success')
            cursor.execute(f"delete from bidding where bidid={buyid}")
            conn.commit()

        cursor.execute(f"INSERT INTO bidding(cropid, buyer, cprice, dated,quantity) VALUES ({id}, '{byer}', {bid},'{dt}',{quantity} );")
        conn.commit()
        cursor.close()
        session.pop('stated', None)
        flash('BID PLACED SUCCESSFULLY','success')

        return redirect(url_for('bhome'))

    a=request.args.get('a')
    cursor=conn.cursor()
    import datetime
    dt = datetime.date.today()
    dt = dt.isoformat()

    cursor.execute(  f"select cropid,crop,baseprice,quantity,description,enddate from cropinfo where cropid={a} and enddate>='{dt}' ")

    crop=cursor.fetchone()

    return render_template('viewcrop.html',crop=crop,form=form)


if(__name__== '__main__'):
        app.run(debug=True)


"""
files = ['file1.txt', 'file2.txt', 'file3.txt']
for f in files:
    shutil.copy(f, 'dest_folder')
os.remove(path)
rename(fname, fname.replace(name, '', 1))"""