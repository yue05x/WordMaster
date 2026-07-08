import bcrypt
from functools import wraps

from flask import g, jsonify, request

from auth.jwt_utils import decode_token
from models import User, db


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"code": 401, "message": "未登录或令牌无效"}), 401

        token = auth_header[7:]
        payload = decode_token(token)
        if not payload:
            return jsonify({"code": 401, "message": "登录已过期，请重新登录"}), 401

        user = db.session.get(User, payload["user_id"])
        if not user or user.status != 1:
            return jsonify({"code": 401, "message": "用户不存在或已被禁用"}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated
