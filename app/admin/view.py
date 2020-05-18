from app.admin import admin
from app.admin.form import *
from app.models import *
from flask import session, render_template, url_for, flash, redirect, request, send_from_directory
from app.setting import UPLOAD_PATH
from app.utlis import getMsg
import os

def adminLoginConfirm(username):
    if session.get("username") != username:
        return redirect(url_for("admin.adminLogin", next=request.url))


@admin.route('/login', methods=['GET', 'POST'])
def adminLogin():
    form = adminLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        admin = Admin.query.filter_by(username=username)
        if admin.count() == 0:
            flash('用户不存在')

        else:
            print(admin.first().checkPassword(password))
            if admin.first().checkPassword(password):
                session['username'] = username
                return redirect(url_for('admin.adminIndex', username=username))
            else:
                flash('密码错误')

    return render_template('adminLogin.html', form=form)



@admin.route('/index/<username>')
def adminIndex(username):
    adminLoginConfirm(username)
    try:
        message = session['message']
        session.pop('message')
    except:
        message = None
    return render_template('adminIndex.html', username=username, message=message)


@admin.route('/getnewdata/<username>')
def adminGetNewData(username):
    adminLoginConfirm(username)
    try:
        getMsg()
        session['message'] = '获取成功'
    except:
        session['message'] = '获取失败'

    return redirect(url_for('admin.adminIndex', username=username))


@admin.route('/changedata/<username>', methods=['GET', 'POST'])
def adminChangeData(username):
    adminLoginConfirm(username)
    # form = timeChooseForm()
    # if form.validate_on_submit():
    #     year = form.year.data
    #     month = form.month.data
    #     day = form.day.data
    #     print(year, '/', month, '/', day)
    #     filename = year + '_' + month + '_' + day + '.json'
    #     path = UPLOAD_PATH + filename
    #     print(path)
    #     print(os.path.exists(path))
    #     return redirect(url_for("admin.adminChangeData", form=form, username=username, filename=filename))
    # file = request.args.get('filename')
    filelist = os.listdir(UPLOAD_PATH)
    print(filelist)
    return render_template("adminChangeData.html", username=username, filelist=filelist)


@admin.route('/datadownload/<filename>')
def adminDataDownload(filename):
    return send_from_directory(UPLOAD_PATH, filename, as_attachment=True)

@admin.route('/dataupload/<username>/<filename>', methods=['POST','GET'])
def adminDataUpload(filename, username):
    adminLoginConfirm(username)
    form = fileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        print(file.filename)
        os.remove(UPLOAD_PATH + filename)
        file.save(os.path.join(UPLOAD_PATH, filename))
        flash('上传成功')
    return render_template('fileupload.html', form=form, filename=filename, username=username)


@admin.route('/commentcontrol/<username>', methods=['GET'])
def commentControl(username):
    cmts = []
    comments = Comment.query.all()
    for comment in comments:
        subcmt = []
        subcomments = subComment.query.filter_by(parentCommentId=comment.id).all()
        for subcomment in subcomments:
            user1 = User.query.get(subcomment.userId)
            temp1 = {
                'username': user1.id,
                'text': subcomment.text,
                'uploadtime': subcomment.uploadTime
            }
            subcmt.append(temp1)
        user2 = User.query.get(comment.userId)
        temp2 = {
            'username': user2.id,
            'text': comment.text,
            'uploadtime': comment.uploadTime,
            'subcomments': subcmt
        }
        cmts.append(temp2)
    return render_template("adminCommentControl.html", cmts = cmts, username=username)