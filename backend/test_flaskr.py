import unittest

from flask import json
from flask_sqlalchemy import SQLAlchemy

from flaskr.__init__ import create_app
from tables import *


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student', 'george', 'localhost:5432',
                                                               self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_200(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_categories_404(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('categories', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_questions_200(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)
        self.assertIn('totalQuestions', data)
        self.assertIn('categories', data)
        self.assertIn('currentCategory', data)

    def test_get_questions_200(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertIn('questions', data)
        self.assertIn('totalQuestions', data)
        self.assertIn('categories', data)
        self.assertIn('currentCategory', data)

    def test_get_questions_404(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('questions', data)
        self.assertNotIn('totalQuestions', data)
        self.assertNotIn('categories', data)
        self.assertNotIn('currentCategory', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_delete_question_200(self):
        dummy_question = Question(question='What is your quest?',
                                  answer='To seek the Holy Grail!',
                                  difficulty=1,
                                  category=1)
        db.session.add(dummy_question)
        db.session.commit()
        dummy_question_id = dummy_question.id
        res = self.client().delete(f'/questions/delete/' + str(dummy_question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('deletedQuestion', data)
        self.assertEqual(data['deletedQuestion'], dummy_question_id)

    def test_delete_question_404(self):
        res = self.client().delete('/questions/delete/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('deletedQuestion', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_search_question_200(self):
        search_term = {'searchTerm': 'title'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)
        self.assertIn('totalQuestions', data)
        self.assertIn('currentCategory', data)

    def test_search_question_404(self):
        search_term = {'searchTerm': 'lalalolo'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('questions', data)
        self.assertNotIn('totalQuestions', data)
        self.assertNotIn('currentCategory', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_search_question_422(self):
        res = self.client().post('/questions/search', json={'searchTerm': None})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertNotIn('questions', data)
        self.assertNotIn('totalQuestions', data)
        self.assertNotIn('currentCategory', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unable to process request')

    def test_search_question_500(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 500)
        self.assertNotIn('questions', data)
        self.assertNotIn('totalQuestions', data)
        self.assertNotIn('currentCategory', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 500)
        self.assertEqual(data['message'], 'Internal Server Error')

    def test_create_question_200(self):
        param = {"question": "How are you?",
                 "answer": "Great",
                 "category": "1",
                 "difficulty": "1",
                 }
        res = self.client().post('/questions', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['newQuestionQuestion'], param["question"])
        self.assertEqual(data['newQuestionAnswer'], param["answer"])
        self.assertEqual(data['newQuestionCategory'], param["category"])
        self.assertEqual(data['newQuestionDifficulty'], param["difficulty"])

    def test_create_question_422(self):
        param = {"question": None,
                 "answer": None,
                 "category": None,
                 "difficulty": None,
                 }
        res = self.client().post('/questions', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertNotIn('newQuestionQuestion', data)
        self.assertNotIn('newQuestionAnswer', data)
        self.assertNotIn('newQuestionCategory', data)
        self.assertNotIn('newQuestionDifficulty', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unable to process request')

    def test_create_question_500(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 500)
        self.assertNotIn('newQuestionQuestion', data)
        self.assertNotIn('newQuestionAnswer', data)
        self.assertNotIn('newQuestionCategory', data)
        self.assertNotIn('newQuestionDifficulty', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 500)
        self.assertEqual(data['message'], 'Internal Server Error')

    def test_get_category_questions_200(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)
        self.assertIn('totalQuestions', data)
        self.assertIn('currentCategory', data)
        
    def test_get_category_questions_404(self):
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('questions', data)
        self.assertNotIn('totalQuestions', data)
        self.assertNotIn('currentCategory', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_next_question_200(self):
        param = {'quizCategory': "2",
                 'previousQuestions': ["17", "18", "19"]}
        res = self.client().post('/quizzes', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertIn('question', data)
        self.assertEqual(16, data["question"]["id"])

    def test_get_next_question_422(self):
        param = {'quizCategory': None,
                 'previousQuestions': None}
        res = self.client().post('/quizzes', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertNotIn('question', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unable to process request')

    def test_get_next_question_404(self):
        param = {'quizCategory': "2",
                 'previousQuestions': ["16","17", "18", "19"]}
        res = self.client().post('/quizzes', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertNotIn('question', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')

        



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
