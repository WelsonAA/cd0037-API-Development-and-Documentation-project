import os
import sys

from flask import Flask, request, abort, jsonify, Response, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import and_

from backend.exceptions import *
from backend.tables import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()

            if len(categories) == 0:
                raise NotFoundException

            res = jsonify({'categories': {
                category.id: category.type for category in categories
            }})
            return res
        except NotFoundException:
            abort(404)
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.order_by(Question.id).offset(start).limit(QUESTIONS_PER_PAGE).all()
            if len(questions) == 0:
                raise NotFoundException
            questions_format = [question.format() for question in questions]
            total_questions = Question.query.count()
            current_category_id = questions[0].category
            current_category_string = Category.query.get(current_category_id).type
            categories = Category.query.order_by(Category.id).all()
            categories_format = [category.format() for category in categories]
            response_data = {
                'questions': questions_format,
                'totalQuestions': total_questions,
                'categories': categories_format,
                'currentCategory': current_category_string
            }
            response = Response(json.dumps(response_data, sort_keys=False), content_type='application/json')
            return response
        except NotFoundException:
            abort(404)
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/delete/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        error = False
        try:
            this_question = Question.query.get(question_id)
            if this_question is None:
                raise NotFoundException
            this_question.delete()
        except NotFoundException:
            abort(404)
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            return jsonify({
                'deletedQuestion': question_id
            })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)
            if search_term is None:
                raise MissingDataException
            fetched_questions = Question.query.filter(Question.question.like(f'%{search_term}%')).all()
            if len(fetched_questions) == 0:
                raise NotFoundException()
            current_category_id = fetched_questions[0].category
            current_category_string = Category.query.get(current_category_id).type
            fetched_questions_format = [question.format() for question in fetched_questions]
            total_questions = Question.query.count()
            response_data = \
            {
                'questions': fetched_questions_format,
                'totalQuestions': total_questions,
                'currentCategory': current_category_string
            }
            response = Response(json.dumps(response_data, sort_keys=False), content_type='application/json')
            return response
        except NotFoundException:
            abort(404)
        except MissingDataException:
            abort(422)
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():
        error = False
        try:
            body = request.get_json()
            question = body.get('question', None)
            answer = body.get('answer', None)
            category = body.get('category', None)
            difficulty = body.get('difficulty', None)
            if question is None or answer is None or category is None or difficulty is None:
                raise MissingDataException
            if difficulty is not None:
                difficulty = int(difficulty)
            if category is not None:
                category = int(category)
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()
        except MissingDataException:
            abort(422)
        except Exception as e:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            response_data = \
             {
                'newQuestionQuestion': question,
                'newQuestionAnswer': answer,
                'newQuestionCategory': str(category),
                'newQuestionDifficulty': str(difficulty)
            }
            response = Response(json.dumps(response_data, sort_keys=False), content_type='application/json')
            return response

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        try:
            if Category.query.get(category_id) is None:
                raise NotFoundException
            questions = Question.query.filter_by(category=category_id).all()
            questions_format = [question.format() for question in questions]
            total_questions = Question.query.count()
            current_category_string = Category.query.get(category_id).type
            response_data = {
                'questions': questions_format,
                'totalQuestions': total_questions,
                'currentCategory': current_category_string
            }
            response = Response(json.dumps(response_data, sort_keys=False), content_type='application/json')
            return response
        except NotFoundException:
            abort(404)
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        try:
            body = request.get_json()
            quiz_category = body.get('quizCategory', None)
            if quiz_category is None:
                raise MissingDataException
            if quiz_category is not None:
                quiz_category = int(quiz_category)
            if Category.query.get(quiz_category) is None:
                raise NotFoundException
            previous_questions = body.get('previousQuestions', [])
            previous_questions_int = [int(question) for question in previous_questions]
            possible_questions = Question.query.filter(and_(Question.category == quiz_category,
                                                            Question.id.notin_(previous_questions))).all()
            if len(possible_questions) == 0:
                raise NotFoundException
            next_question = random.choice(possible_questions)
            next_question = next_question.format()
            return jsonify({
                'question': next_question
            })
        except NotFoundException:
            abort(404)
        except MissingDataException:
            abort(422)
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request",
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(405)
    def invalid_request(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Invalid Request"
        }), 405

    @app.errorhandler(422)
    def unable_to_process(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unable to process request"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app


create_app()
