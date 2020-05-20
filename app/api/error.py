from flask import jsonify


def dataIncomplete(msg="参数不完整"):
    return jsonify(
        {
            "status": 1001,
            "msg": msg
        }
    )


def duplicateData(msg="用户名存在和他人重复"):
    return jsonify(
        {
            "status": 1002,
            "msg": msg
        }
    )

def invalidToken(msg="无效token"):
    return jsonify(
        {
            "status": 1003,
            "msg": msg
        }
    )

def noneObject(msg="对象不存在"):
    return jsonify(
        {
            "status": 1004,
            "msg": msg
        }
    )


def permissionDenied(msg="没有权限"):
    return jsonify(
        {
            "status": 1005,
            "msg": msg
        }
    )