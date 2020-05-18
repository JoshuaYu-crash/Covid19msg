from app.api import api
from flask import request, jsonify
from app.models import *
from app.utlis import generate_token, certify_token


# 注册
@api.route('/register', methods=['POST'])
def userRegister():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        # 信息不完整
        pass
    if User.query.filter_by(username=username).count() != 0:
        # 用户名存在
        pass
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
        'username': username,
        'token':token
    })


# 登录
@api.route('/login', methods=['POST'])
def userLogin():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        # 信息不完整
        print(1)
    if User.query.filter_by(username=username).count() == 0:
        # 账号不存在
        print(2)
    user = User.query.filter_by(username=username).first()
    if user.checkPassword(password):
        token = generate_token(username)
        user.token = token
        db.session.commit()
        return jsonify(
            {
                'username': username,
                'token': token
            }
        )
    else:
        # 密码错误
        pass


# 发评论
@api.route('/comment', methods=['POST'])
def makeComment():
    # 验证token
    token = request.json.get('token')
    user = User.query.filter_by(token=token).first()
    if user is None or certify_token(user.username, token):
        # token无效
        pass

    text = request.json.get('text')
    if text is None:
        # 重要参数不能为空
        pass

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
            'id': comment.id,
            'username': user.username,
            'token': token,
            'text': text,
            'uploadTime': comment.uploadTime
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
        pass

    text = request.json.get('text')
    parentId = request.json.get('parentid')
    if text is None or parentId is None:
        # 重要参数不能为空
        pass
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
            'id': subcmt.id,
            'username': user.username,
            'token': token,
            'text': text,
            'uploadTime': subcmt.uploadTime
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
    return jsonify(
        {
            'comments': cmts
        }
    )



# 删除评论

