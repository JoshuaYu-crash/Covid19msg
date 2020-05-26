from app.api import api
from flask import request, jsonify
from app.models import *
from app.utlis import generate_token, certify_token, getMsg
from app.setting import UPLOAD_PATH
from app.api.error import *


# 注册
@api.route('/register', methods=['POST'])
def userRegister():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        # 信息不完整
        return dataIncomplete()
    if User.query.filter_by(username=username).count() != 0:
        # 用户名存在
        return duplicateData()
    token = generate_token(username)
    user = User(
        username=username,
        token = token
    )
    password = user.makePassword(password)
    user.password = password
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'status':0,
        'data': {
            'username': username,
            'token': token
        }
    })


# 登录
@api.route('/login', methods=['POST'])
def userLogin():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        # 信息不完整
        return dataIncomplete()
    if User.query.filter_by(username=username).count() == 0:
        # 账号不存在
        return noneObject("账号不存在")
    user = User.query.filter_by(username=username).first()
    if user.checkPassword(password):
        token = generate_token(username)
        user.token = token
        db.session.commit()
        return jsonify(
            {
                'status': 0,
                'data': {
                    'username': username,
                    'userid': user.id,
                    'token': token
                }
            }
        )
    else:
        # 密码错误
        invalidToken("密码错误")


# 发评论
@api.route('/comment', methods=['POST'])
def makeComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        return invalidToken()

    text = request.json.get('text')
    if text is None:
        # 重要参数不能为空
        return dataIncomplete()

    # 提交评论
    comment = Comment(
        text=text,
        userId=user.id
    )
    db.session.add(comment)

    # 生成新token
    token = generate_token(user.username)
    user.token=token

    db.session.commit()

    return jsonify(
        {
            'status': 0,
            'data': {
                'id': comment.id,
                'username': user.username,
                'token': token,
                'text': text,
                'uploadTime': comment.uploadTime
            }

        }
    )




# 评论别人评论
@api.route('/subcomment', methods=['POST'])
def makeSubComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        return invalidToken()

    text = request.json.get('text')
    parentId = request.json.get('parentid')
    if text is None or parentId is None:
        # 重要参数不能为空
        return dataIncomplete()

    if Comment.query.get(parentId) is None:
        # 评论不存在
        noneObject()
    subcmt = subComment(
        text=text,
        userId=user.id,
        parentCommentId=parentId
    )
    db.session.add(subcmt)

    # 生成新token
    token = generate_token(user.username)
    user.token = token

    db.session.commit()
    return jsonify(
        {
            'status': 0,
            'data': {
                'id': subcmt.id,
                'username': user.username,
                'token': token,
                'text': text,
                'uploadTime': subcmt.uploadTime
            }

        }
    )


# 获取评论
@api.route('/getcomment', methods=['GET'])
def getComment():
    cmts = []
    comments = Comment.query.all()
    for comment in comments:
        subcmt = []
        subcomments = subComment.query.filter_by(parentCommentId=comment.id).all()
        for subcomment in subcomments:
            user1 = User.query.get(subcomment.userId)
            temp1 = {
                'userid': user1.id,
                'username': user1.username,
                'text': subcomment.text,
                'subcommentid': subcomment.id,
                'uploadtime': subcomment.uploadTime,
                'star':subcomment.star
            }
            subcmt.append(temp1)
        user2 = User.query.get(comment.userId)
        temp2 = {
            'userid': user2.id,
            'username': user2.username,
            'text': comment.text,
            'commentid': comment.id,
            'uploadtime': comment.uploadTime,
            'star':comment.star,
            'subcomments': subcmt
        }
        cmts.append(temp2)
    return jsonify(
        {
            'status': 0,
            'data': {
                'comments': cmts
            }

        }
    )



# 删除父评论
@api.route('/deletecomment', methods=['POST'])
def deleteComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        return invalidToken()

    commentId = request.json.get('commentid')

    comment = Comment.query.get(commentId)

    if comment.userId != user.id:
        # 没有权限
        return permissionDenied()
    subComment.query.filter_by(parentCommentId=comment.id).delete()
    db.session.delete(comment)

    # 生成新token
    token = generate_token(user.username)
    user.token = token

    db.session.commit()

    return jsonify(
        {
            'status':0,
            'data': {
                'token': token
            }
        }
    )


# 删除子评论
@api.route('/deletesubcomment', methods=['POST'])
def deleteSubComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        return invalidToken()

    subCommentId = request.json.get('subcommentid')

    subcomment = subComment.query.get(subCommentId)
    db.session.delete(subcomment)

    # 生成新token
    token = generate_token(user.username)
    user.token = token

    db.session.commit()

    return jsonify(
        {
            'status':0,
            'data': {
                'token': token
            }
        }
    )






# 获取数据
@api.route('/getmsg', methods=['POST', 'GET'])
def getMsg():
    if request.method == 'POST':
        year = request.json.get('year')
        month = request.json.get('month')
        day = request.json.get('day')
        if year is not None and month is not None and day is not None:
            if month < 10:
                month = '0' + str(month)
            filename = UPLOAD_PATH + str(year) + '_' + month + '_' + str(day) + '.json'
            with open(filename, 'r', encoding='gbk') as f:
                msg = f.read()
        else:
            filename = UPLOAD_PATH + datetime.now().strftime('%Y_%m_%d') + '.json'
            with open(filename, 'r', encoding='gbk') as f:
                msg = f.read()
    else:
        try:
            filename = UPLOAD_PATH + datetime.now().strftime('%Y_%m_%d') + '.json'
            with open(filename, 'r', encoding='gbk') as f:
                msg = f.read()
        except:
            getMsg()
            filename = UPLOAD_PATH + datetime.now().strftime('%Y_%m_%d') + '.json'
            with open(filename, 'r', encoding='gbk') as f:
                msg = f.read()
    return msg

# 父评论点赞
@api.route('/starcomment', methods=['POST'])
def starComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        return invalidToken()

    commentId = request.json.get('commentid')
    comment = Comment.query.get(commentId)
    if comment is None:
        # 没有该评论
        return noneObject()

    userstars = userStar.query.filter_by(userId=user.id).all()
    check = 0
    for userstar in userstars:
        if userstar.commentId == comment.id:
            check = 1
            break
    if check:
        # 已经点赞了
        permissionDenied()

    comment.star += 1
    userstar = userStar(
        userId=user.id,
        commentType=0,
        commentId=comment.id
    )
    db.session.add(userstar)

    # 生成新token
    token = generate_token(user.username)
    user.token = token

    db.session.commit()

    return jsonify(
        {
            'status':0,
            'data': {
                'token': token
            }
        }
    )




# 子评论点赞
@api.route('/starsubcomment', methods=['POST'])
def starSubComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        return invalidToken()

    subCommentId = request.json.get('subcommentid')
    subcomment = Comment.query.get(subCommentId)
    if subcomment is None:
        # 没有该评论
        return noneObject()

    userstars = userStar.query.filter_by(userId=user.id).all()
    check = 0
    for userstar in userstars:
        if userstar.subCommentId == subcomment.id:
            check = 1
            break
    if check:
        # 已经点赞了
        permissionDenied("不能重复点赞")

    subcomment.star += 1
    userstar = userStar(
        userId=user.id,
        commentType=1,
        subCommentId=subcomment.id
    )
    db.session.add(userstar)

    # 生成新token
    token = generate_token(user.username)
    user.token = token

    db.session.commit()

    return jsonify(
        {
            'status':0,
            'data': {
                'token': token
            }
        }
    )