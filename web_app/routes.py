import os, json
from flask import render_template, flash, session, redirect, abort, request, url_for, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

from flask_migrate import current
from web_app import app, db
from web_app.models import Admin, User, Document
from web_app.forms import AdminLoginForm, RegisterForm, UserLoginForm, NewDocumentForm
from web_app.token import UserIDToken
from web_app.utils import btn_map, change_user_status, delete_doc, update_session, save_pdf, delete_doc, preview_doc, create_admin
from web_app.chatbot import chat_handler, contruct_svb


@app.before_request
def before_request():
    if request.endpoint == 'static' and 'docs' in request.path:
        if not current_user.is_authenticated and session.get('status') != 'member':
            return abort(403)


@app.route('/app')
def home():
    update_session()
    return render_template('home.html', liffId=app.config['LIFF_ID'])


@app.route('/app/register', methods=['GET', 'POST'])
def register():
    if not session.get('is_verified') and not session.get('userId'):
        session['next'] = 'register'
        return redirect(url_for('login', _external=True, _scheme='https'))
    if session['status'] == 'requested' and request.method == 'GET':
        return render_template('register_success.html', liffId=app.config['LIFF_ID'])
    if session['status'] == 'member' or session['status'] == 'blocked':
        return render_template('error.html', error= "ไม่สามารถลงทะเบียนได้ เนื่องจากท่านเป็นสมาชิก LINE TSE OA อยู่แล้ว")
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(userId=session['userId']).first() != None: # Check if already registered
            flash('บัญชีไลน์นี้ได้ลงทะเบียนหรือมีผู้ใช้งานแล้ว หากท่านเป็นเจ้าของบัญชี โปรดติดต่อเจ้าหน้าที่', 'danger')
            return render_template('register.html', title="ลงทะเบียน", form=form)
        elif User.query.filter_by(name=form.name.data, surname=form.surname.data).first() != None:  # Check if name surname
            flash('ชื่อ - นามสกุล นี้ถูกใช้แล้ว หากท่านเป็นเข้าของบัญชี โปรดติดต่อเจ้าหน้าที่', 'danger')
            return render_template('register.html', title="ลงทะเบียน", form=form)
        else:
            newUser = User(
                userId = session['userId'],
                name = form.name.data.strip(),
                surname = form.surname.data.strip(),
                status = "requested",
                displayName = session['display_name'],
                dealer = form.dealer.data,
                position = "TIS group" if form.dealer.data == "TIS group" else form.position.data,
                pictureUrl = session['picture'],
                log = f"|{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}#requested"
            )
            print(newUser)
            db.session.add(newUser)
            try:
                db.session.commit()
                print("Added to database")  
            except Exception as exc:
                print("Failed to add to database: ", exc)
                return "Database error"
            session['status'] = 'requested'
            return render_template('register_success.html')
    return render_template('register.html', title="ลงทะเบียน", liffId=app.config['LIFF_ID'], form = form)


@app.route('/app/login', methods=['GET', 'POST'])
def login():
    if session.get('is_verified'):
        if 'docs' in session.get('next'):
            path = session.get('next').split('/')
            return redirect(url_for(path[0], hex=path[1], _external=True, _scheme='https'))
        return redirect(url_for(session.get('next') if session.get('next') is not None else 'home', _external=True, _scheme='https'))
    else:
        session['is_verified'] = False
    form = UserLoginForm()
    if form.validate_on_submit():
        try:
            userIDToken = UserIDToken(form.userIDToken.data, app.config['LIFF_CHANNEL_ID'])
            getOS = form.getOS.data
            isInClient = form.isInClient.data
            getFriendShip = form.getFriendShip.data
        except:
            abort(401)
        if getOS not in ['ios', 'android'] or isInClient != "true":
            return render_template('error.html', error="Platform error")
        if getFriendShip != "true":
            return render_template('error.html', error="Friendship error")
        userIDToken.verify()
        if not userIDToken.is_valid:
            return render_template('error.html', error= userIDToken.err_msg)
        session['is_verified'] = True
        session['userId'] = userIDToken.detail['sub']
        # Check membership
        user = User.query.filter_by(userId = session['userId']).first()
        session['status'] = "guest" if not user else user.status
        if session['status'] == "guest":
            session['display_name'] = userIDToken.detail['name']
            session['picture'] = userIDToken.detail['picture']
        else:
            #Update profile pic
            if userIDToken.detail['picture'] != user.pictureUrl:
                user.pictureUrl = userIDToken.detail['picture']
                try:
                    db.session.commit()
                    print('Updated profile url!')
                except:
                    pass
            if userIDToken.detail['name'] != user.displayName:
                user.displayName = userIDToken.detail['name']
                try:
                    db.session.commit()
                    print('Updated display name!')
                except:
                    pass
        if 'docs' in session.get('next'):
            path = session.get('next').split('/')
            return redirect(url_for(path[0], hex=path[1], _external=True, _scheme='https'))
        return redirect(url_for(session.get('next') if session.get('next') is not None else 'home', _external=True, _scheme='https'))
    return render_template('login.html', form=form, liffId=app.config['LIFF_ID'])


@app.route('/app/docs/<hex>')
def docs(hex):
    if not session.get('is_verified'):
        session['next'] = 'docs/' + hex
        return redirect(url_for('login', _external=True, _scheme='https'))
    if session['status'] != 'member':
        abort(403)
    user = User.query.filter_by(userId=session['userId']).first()
    if not user:
        abort(403)
    res = preview_doc(hex)
    if not res[0]:
        print(res[1])
        abort(res[2])
    watermark = f"เอกสารสำหรับ {user.name} {user.surname}"
    return render_template('docs.html',title=res[2] , watermark=watermark, hex=hex, pageNum=res[1])


@app.route('/app/svb/recent')
def recent_svb():
    if not session.get('is_verified'):
        session['next'] = 'recent_svb'
        return redirect(url_for('login', _external=True, _scheme='https'))
    if session['status'] != 'member':
        if session['status'] == 'requested':
            msg =   {
                'type': 'text',
                'text': 'โปรดรอการยืนยันการลงเบียนเพื่อใช้งานค่ะ'
            }
        else:
            msg =   {
                'type': 'text',
                'text': 'โปรดลงทะเบียนเพื่อใช้งานค่ะ'
            }
    else:
        content = contruct_svb()
        if content[0]:
            msg = {
                "type": "flex",
                "altText":'ข่าวสารบริการอีซูซุฉบับล่าสุด',
                "contents":content[1]
            }
        else:
            msg = {
                'type': 'text',
                'text': 'ไม่พบข่าวสารบริการ โปรดตรวจสอบบนระบบคุณใจดีอีกครั้ง'
            }
    return render_template('recent_svb.html', liffId=app.config['LIFF_ID'], msg=msg) 


######################################################################################## ADMIN section


@app.route('/admin', methods=['GET'])
@login_required
def admin_home():
    return render_template('admin_home.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # if Admin.query.first() is None:
    #     create_admin()
    if current_user.is_authenticated:
        return redirect(url_for('admin_home'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is not None and admin.verify_password(form.password.data):
            login_user(admin, form.remember_me.data)
            next = request.args.get('next')
            return redirect(next if next is not None else url_for('admin_home'))
        flash('Invalid username or password', 'danger')
    return render_template('admin_login.html', form=form)


@app.route('/admin/logout', methods=['GET'])
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/admin/users', methods=['GET'])
@login_required
def users(): 
    if request.args.get('action') and request.args.get('userId'):
        userId = request.args.get('userId')
        action = request.args.get('action')
        user = User.query.filter_by(userId=userId).first()
        if user:
            result = change_user_status(user, action)
            if result[0]:
                flash(result[1], 'success')
            else:
                flash(result[1], 'danger')
        else:
            flash('User not found on the server !', "danger")
        return redirect(url_for('users'))
    return render_template('users.html', title='TSE LINE OA User List', btn_map=btn_map,
                users= User.query.all())


@app.route('/admin/documents', methods=['GET', 'POST'])
@login_required
def documents():
    form = NewDocumentForm()
    if request.method == 'GET' and request.args.get('hex') and request.args.get('action'):
        hex = request.args.get('hex')
        action = request.args.get('action')
        if action == "delete":
            res = delete_doc(hex)
            if res[0]:
                flash('Document has been deleted!', 'success')
            else:
                flash(res[1], 'danger')
            return redirect(url_for('documents'))
    if form.validate_on_submit():
        form = NewDocumentForm()
        res = save_pdf(form)
        if res[0]: # success
            flash('New document has been uploaded!', "success")
        else:
            flash(res[1], "danger")
        return redirect(url_for('documents'))
    return render_template('documents.html', form=form, documents=enumerate(Document.query.all(), start=1))


@app.route('/admin/documents/preview')
@login_required
def preview():
    hex = request.args.get('hex')
    res = preview_doc(hex)
    if res[0]:
        numPage = res[1]
        return render_template('preview.html', hex=hex, title=res[2], numPage=numPage)
    else:
        flash(res[1], 'danger')
        return redirect(url_for('documents'))


##############################  Error handler

@app.errorhandler(403)
def error_403(error):
    return render_template('error_403.html'), 403  # Second value as a status code; Default is 200


##############################  LINE BOT


@app.route('/msg/callback', methods=['POST'])
def callback():
    try:
        chat_handler()
    except:
        pass
    return 'ok', 200

       
##############################  Load tester

@app.route('/loaderio-d014757b4c21bf56a857270d50153001/')
def load_test_verify():
    return send_from_directory('static/verify', 'loaderIO.txt')

