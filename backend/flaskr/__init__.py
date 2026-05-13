from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/*": {"origins": "*"}})
    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,POST,PUT,DELETE,OPTIONS"
        )
        return response

    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_questions = [question.format() for question in selection]
        return formatted_questions[start:end]

    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        return {category.id: category.type for category in categories}

    @app.route("/categories", methods=["GET"])
    def get_categories_endpoint():
        categories = get_categories()
        if not categories:
            abort(404)
        return jsonify({
            "success": True,
            "categories": categories
        })

    @app.route("/questions", methods=["GET"])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(selection),
            "categories": get_categories(),
            "current_category": None
        })

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)
        question.delete()
        return jsonify({
            "success": True,
            "deleted": question_id
        })

    @app.route("/questions/<int:question_id>", methods=["PUT"])
    def update_question(question_id):
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)

        data = request.get_json()
        if data is None:
            abort(400)

        allowed_fields = {"question", "answer", "category", "difficulty"}
        if not any(field in data for field in allowed_fields):
            abort(400)

        updates = {}
        if "question" in data:
            if not data["question"]:
                abort(400)
            updates["question"] = data["question"]

        if "answer" in data:
            if not data["answer"]:
                abort(400)
            updates["answer"] = data["answer"]

        try:
            if "category" in data:
                if not data["category"]:
                    abort(400)
                updates["category"] = int(data["category"])

            if "difficulty" in data:
                if not data["difficulty"]:
                    abort(400)
                updates["difficulty"] = int(data["difficulty"])
        except ValueError:
            abort(422)

        for field, value in updates.items():
            setattr(question, field, value)

        try:
            question.update()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            "success": True,
            "updated": question_id,
            "question": question.format()
        })

    @app.route("/questions", methods=["POST"])
    def create_or_search_questions():
        data = request.get_json()
        if data is None:
            abort(400)

        search_term = data.get("searchTerm")
        if search_term is not None:
            if not isinstance(search_term, str) or search_term.strip() == "":
                abort(400)
            selection = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).order_by(Question.id).all()
            if len(selection) == 0:
                abort(404)
            return jsonify({
                "success": True,
                "questions": [question.format() for question in selection],
                "total_questions": len(selection),
                "current_category": None
            })

        question_text = data.get("question")
        answer_text = data.get("answer")
        category = data.get("category")
        difficulty = data.get("difficulty")

        if (
            not question_text
            or not answer_text
            or not category
            or not difficulty
        ):
            abort(400)

        created_id = None
        try:
            new_question = Question(
                question=question_text,
                answer=answer_text,
                category=int(category),
                difficulty=int(difficulty)
            )
            new_question.insert()
            created_id = new_question.id
        except Exception:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            "success": True,
            "created": created_id
        })

    @app.route(
        "/categories/<int:category_id>/questions",
        methods=["GET", "POST"]
    )
    def get_questions_by_category(category_id):
        category = db.session.get(Category, category_id)
        if category is None:
            abort(404)
        selection = Question.query.filter_by(
            category=int(category_id)
        ).order_by(Question.id).all()
        if len(selection) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "questions": [question.format() for question in selection],
            "total_questions": len(selection),
            "current_category": category.type
        })

    @app.route("/quizzes", methods=["POST"])
    def get_quiz_question():
        data = request.get_json()
        if data is None:
            abort(400)

        previous_questions = data.get("previous_questions")
        quiz_category = data.get("quiz_category")

        if previous_questions is None or quiz_category is None:
            abort(400)

        if not isinstance(previous_questions, list):
            abort(400)

        category_id = (
            quiz_category.get("id")
            if isinstance(quiz_category, dict)
            else None
        )
        if category_id in (0, None, "0"):
            query = Question.query
        else:
            query = Question.query.filter_by(category=int(category_id))

        available_questions = query.filter(
            Question.id.notin_(previous_questions)
        ).all()

        if len(available_questions) == 0:
            return jsonify({
                "success": True,
                "question": None
            })

        question = random.choice(available_questions)
        return jsonify({
            "success": True,
            "question": question.format()
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
