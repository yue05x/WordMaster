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


if __name__ == "__main__":
    unittest.main()
