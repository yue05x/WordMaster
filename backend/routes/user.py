from flask import Blueprint, current_app, g, jsonify, request

from auth.decorators import hash_password, login_required, verify_password
from auth.jwt_utils import create_token
from models import User, db

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if len(username) < 3 or len(password) < 6:
        return jsonify({"code": 400, "message": "用户名至少3位，密码至少6位"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"code": 400, "message": "用户名已存在"}), 400
    role = data.get("role", "student")
    if role not in {"student", "teacher"}:
        return jsonify({"code": 400, "message": "请选择正确的注册身份"}), 400
    if role == "teacher" and data.get("teacher_code") != current_app.config["TEACHER_CODE"]:
        return jsonify({"code": 400, "message": "教师邀请码错误"}), 400
    user = User(username=username, password=hash_password(password),
                nickname=(data.get("nickname") or username).strip(),
                email=(data.get("email") or "").strip() or None, role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({"code": 200, "message": "注册成功", "data": {
        "token": create_token(user.id, user.username), "user": user.to_dict()}})


@user_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    if role not in {"student", "teacher"}:
        return jsonify({"code": 400, "message": "请选择登录身份"}), 400
    user = User.query.filter_by(username=(data.get("username") or "").strip()).first()
    if not user or not verify_password(data.get("password") or "", user.password):
        return jsonify({"code": 401, "message": "用户名或密码错误"}), 401
    if user.role != role:
        return jsonify({"code": 403, "message": f"该账号不是{'教师' if role == 'teacher' else '学生'}账号"}), 403
    return jsonify({"code": 200, "message": "登录成功", "data": {
        "token": create_token(user.id, user.username), "user": user.to_dict()}})


@user_bp.get("/info")
@login_required
def info():
    return jsonify({"code": 200, "data": g.current_user.to_dict()})


@user_bp.post("/logout")
@login_required
def logout():
    return jsonify({"code": 200, "message": "已退出登录"})
