import os
import unittest

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = os.environ.get("TRIVIA_TEST_DB_NAME", "trivia_test")
        self.database_user = os.environ.get("TRIVIA_DB_USER", "postgres")
        self.database_password = os.environ.get("TRIVIA_DB_PASSWORD", "password")
        self.database_host = os.environ.get("TRIVIA_DB_HOST", "localhost:5432")
        self.database_path = os.environ.get(
            "TEST_DATABASE_URL",
            f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"
        )

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()
            self.categories = [
                Category(type="Science"),
                Category(type="Art"),
                Category(type="History")
            ]
            db.session.add_all(self.categories)
            db.session.commit()
            self.category_ids = [category.id for category in self.categories]
            self.category_types = [category.type for category in self.categories]

            self.questions = []
            for i in range(12):
                category_id = self.category_ids[i % len(self.category_ids)]
                question = Question(
                    question=f"Question {i + 1}?",
                    answer=f"Answer {i + 1}",
                    category=category_id,
                    difficulty=(i % 5) + 1
                )
                self.questions.append(question)
            db.session.add_all(self.questions)
            db.session.commit()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            try:
                db.drop_all()
            except Exception:
                db.session.rollback()
                Question.query.delete()
                Category.query.delete()
                db.session.commit()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_success(self):
        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["categories"]) > 0)

    def test_get_categories_not_found(self):
        with self.app.app_context():
            Question.query.delete()
            Category.query.delete()
            db.session.commit()

        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_questions_success(self):
        response = self.client.get("/questions?page=1")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]) <= 10)
        self.assertTrue(data["total_questions"] >= 12)
        self.assertTrue(len(data["categories"]) > 0)

    def test_get_questions_out_of_range(self):
        response = self.client.get("/questions?page=100")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_delete_question_success(self):
        with self.app.app_context():
            question = Question(
                question="Delete me?",
                answer="Yes",
                category=self.category_ids[0],
                difficulty=1
            )
            question.insert()
            question_id = question.id

        response = self.client.delete(f"/questions/{question_id}")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

        with self.app.app_context():
            deleted = db.session.get(Question, question_id)
            self.assertIsNone(deleted)

    def test_delete_question_not_found(self):
        response = self.client.delete("/questions/99999")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_create_question_success(self):
        payload = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": self.category_ids[1],
            "difficulty": 2
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

    def test_create_question_bad_request(self):
        payload = {
            "question": "Incomplete payload",
            "answer": "Missing category and difficulty"
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])

    def test_search_questions_success(self):
        payload = {"searchTerm": "Question 1"}
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]) > 0)

    def test_search_questions_not_found(self):
        payload = {"searchTerm": "NoMatchForThis"}
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_questions_by_category_success(self):
        category_id = self.category_ids[0]
        response = self.client.get(f"/categories/{category_id}/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]) > 0)
        self.assertEqual(data["current_category"], self.category_types[0])

    def test_get_questions_by_category_not_found(self):
        response = self.client.get("/categories/99999/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_quiz_question_success(self):
        category_id = self.category_ids[0]
        payload = {
            "previous_questions": [],
            "quiz_category": {"id": category_id, "type": self.category_types[0]}
        }
        response = self.client.post("/quizzes", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["question"])
        self.assertEqual(data["question"]["category"], str(category_id))

    def test_get_quiz_question_bad_request(self):
        response = self.client.post("/quizzes", json={})
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
