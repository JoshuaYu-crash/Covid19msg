import os

# MySQL数据库连接
SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1/covidmsg"

# 数据库追踪关闭
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 密钥设置
SECRET_KEY = "SecretKey"

# JSON自动排序关闭
JSON_SORT_KEYS = False

# 上传文件位置
UPLOAD_PATH = os.path.join(os.path.dirname((__file__)), 'CovidMessage\\')

# 允许上传的图片
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.JPG', '.PNG', '.gif', '.GIF']