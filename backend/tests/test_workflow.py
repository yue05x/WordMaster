import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        self.client = self.app.test_client()

    def register(self, username, role="student"):
        body = {"username": username, "password": "123456", "role": role}
        if role == "teacher":
            body["teacher_code"] = "teacher123"
        response = self.client.post("/api/user/register", json=body)
        self.assertEqual(response.status_code, 200)
        return response.json["data"]["token"]

    @staticmethod
    def headers(token):
        return {"Authorization": f"Bearer {token}"}

    def test_shared_questions_shuffle_grading_and_wordcloud(self):
        teacher = self.register("teacher", "teacher")
        student_a = self.register("student_a")
        student_b = self.register("student_b")
        now = datetime.utcnow()
        response = self.client.post("/api/exams", headers=self.headers(teacher), json={
            "title": "CET4 周测", "question_count": 10, "duration_minutes": 30,
            "start_time": (now - timedelta(minutes=1)).isoformat(),
            "end_time": (now + timedelta(hours=1)).isoformat(),
        })
        exam_id = response.json["data"]["id"]
        a = self.client.post(f"/api/exams/{exam_id}/start", headers=self.headers(student_a)).json["data"]
        b = self.client.post(f"/api/exams/{exam_id}/start", headers=self.headers(student_b)).json["data"]
        order_a = [q["question_id"] for q in a["questions"]]
        order_b = [q["question_id"] for q in b["questions"]]
        self.assertEqual(set(order_a), set(order_b))
        self.assertNotEqual(order_a, order_b)
        answers = [{"question_id": q["question_id"], "answer": "错误答案"} for q in a["questions"]]
        result = self.client.post(f"/api/exams/attempts/{a['attempt_id']}/submit",
            headers=self.headers(student_a), json={"answers": answers})
        self.assertEqual(result.status_code, 200)
        cloud = self.client.get("/api/statistics/wordcloud?days=7", headers=self.headers(student_a))
        self.assertEqual(len(cloud.json["data"]), 10)

    def test_role_validation_and_login_identity(self):
        bad_teacher = self.client.post("/api/user/register", json={
            "username": "bad_teacher", "password": "123456",
            "role": "teacher", "teacher_code": "wrong-code",
        })
        self.assertEqual(bad_teacher.status_code, 400)
        self.assertIn("邀请码", bad_teacher.json["message"])

        self.register("real_teacher", "teacher")
        wrong_role = self.client.post("/api/user/login", json={
            "username": "real_teacher", "password": "123456", "role": "student",
        })
        self.assertEqual(wrong_role.status_code, 403)
        correct_role = self.client.post("/api/user/login", json={
            "username": "real_teacher", "password": "123456", "role": "teacher",
        })
        self.assertEqual(correct_role.status_code, 200)
        self.assertEqual(correct_role.json["data"]["user"]["role"], "teacher")

    def test_teacher_word_and_exam_management(self):
        teacher = self.register("manager", "teacher")
        headers = self.headers(teacher)
        created = self.client.post("/api/words", headers=headers, json={
            "word": "codex", "meaning": "代码助手", "level": "拓展",
        })
        self.assertEqual(created.status_code, 200)
        word_id = created.json["data"]["id"]
        updated = self.client.put(f"/api/words/{word_id}", headers=headers, json={
            "word": "codex", "meaning": "智能代码助手", "level": "拓展",
        })
        self.assertEqual(updated.json["data"]["meaning"], "智能代码助手")
        deleted = self.client.delete(f"/api/words/{word_id}", headers=headers)
        self.assertEqual(deleted.status_code, 200)

        now = datetime.utcnow()
        exam = self.client.post("/api/exams", headers=headers, json={
            "title": "可编辑测试", "question_count": 5, "duration_minutes": 20,
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=2)).isoformat(),
        })
        self.assertEqual(exam.status_code, 200)
        exam_id = exam.json["data"]["id"]
        changed = self.client.put(f"/api/exams/{exam_id}", headers=headers, json={
            "title": "修改后的考试", "duration_minutes": 25,
        })
        self.assertEqual(changed.json["data"]["title"], "修改后的考试")
        removed = self.client.delete(f"/api/exams/{exam_id}", headers=headers)
        self.assertEqual(removed.status_code, 200)

    def test_exam_window_must_cover_duration(self):
        teacher = self.register("time_teacher", "teacher")
        now = datetime.utcnow()
        response = self.client.post("/api/exams", headers=self.headers(teacher), json={
            "title": "错误时间考试", "question_count": 5, "duration_minutes": 30,
            "start_time": now.isoformat(),
            "end_time": (now + timedelta(seconds=10)).isoformat(),
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("不能少于", response.json["message"])


if __name__ == "__main__":
    unittest.main()
