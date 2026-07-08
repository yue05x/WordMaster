from flask import Blueprint, g, jsonify, request

from auth.decorators import hash_password, login_required, verify_password
from auth.jwt_utils import create_token
from models import User, db

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or "").strip()
    email = (data.get("email") or "").strip()

    if not username or len(username) < 3:
        return jsonify({"code": 400, "message": "用户名至少3个字符"}), 400
    if not password or len(password) < 6:
        return jsonify({"code": 400, "message": "密码至少6个字符"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"code": 400, "message": "用户名已存在"}), 400

    user = User(
        username=username,
        password=hash_password(password),
        nickname=nickname or username,
        email=email or None,
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id, user.username)
    return jsonify(
        {
            "code": 200,
            "message": "注册成功",
            "data": {"token": token, "user": user.to_dict()},
        }
    )


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password):
        return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

    if user.status != 1:
        return jsonify({"code": 403, "message": "账号已被禁用"}), 403

    token = create_token(user.id, user.username)
    return jsonify(
        {
            "code": 200,
            "message": "登录成功",
            "data": {"token": token, "user": user.to_dict()},
        }
    )


@user_bp.route("/info", methods=["GET"])
@login_required
def get_user_info():
    return jsonify({"code": 200, "data": g.current_user.to_dict()})


@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    return jsonify({"code": 200, "message": "已退出登录"})
