import unittest
import os
from flask import json
from flask_sqlalchemy import SQLAlchemy

from flaskr.__init__ import create_app
from tables import *
from dotenv import load_dotenv, dotenv_values


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        load_dotenv()
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.db_username = os.getenv("DB_USERNAME")
        self.db_password = os.getenv("DB_PASSWORD")
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.db_username, self.db_password, 'localhost:5432',
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

    def test_get_next_question_200(self):
        def setUp():
            new_question = Question('When was Breaking Bad Season 1 released?', "2008",
                                    2, 1)
            new_question.insert()

        def tearDown():
            Question.query.filter(Question.question == "When was Breaking Bad Season 1 released?").delete()

        setUp()
        param = {'quizCategory': "2",
                 'previousQuestions': ["17", "18", "19"]}
        res = self.client().post('/quizzes', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('question', data)

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
        res = self.client().get('/categories/1/questions')
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

    def test_get_next_question_422(self):
        param = {'quizCategory': None,
                 'previousQuestions': None}
        res = self.client().post('/quizzes', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertNotIn('question', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unable to process request')

    def test_get_next_question_404(self):
        def setUp():
            questions = Question.query.all()
            for question in questions:
                question.delete()
            questions = [Question('What year was US independence?', '1776', 3, 4)]
            for question in questions:
                question.insert()
        def tearDown():
            Question.query.filter(Question.question == 'What year was US independence?').delete()
            questions = [Question('Whose autobiography is entitled ''I Know Why the Caged Bird Sings''?',
                                  'Maya Angelou', 2, 4),
                         Question('What boxer''s original name is Cassius Clay?', 'Muhammad Ali',
                                  1, 4),
                         Question('What movie earned Tom Hanks his third straight Oscar nomination, in 1996?',
                                  'Apollo 13', 4, 5),
                         Question('What actor did author Anne Rice first denounce, then praise in the role of '
                                  'her beloved Lestat?', 'Tom Cruise', 4, 5),
                         Question('What was the title of the 1990 fantasy directed by Tim Burton about a young '
                                  'man with multi-bladed appendages?', 'Edward Scissorhands', 3,
                                  5),
                         Question('Which is the only team to play in every soccer World Cup tournament?',
                                  'Brazil', 3, 6),
                         Question('Which country won the first ever soccer World Cup in 1930?',
                                  'Uruguay', 4, 6),
                         Question('Who invented Peanut Butter?', 'George Washington Carver',
                                  2, 4),
                         Question('What is the largest lake in Africa?', 'Lake Victoria',
                                  2, 3),
                         Question('In which royal palace would you find the Hall of Mirrors?',
                                  'The Palace of Versailles', 3, 3),
                         Question('The Taj Mahal is located in which Indian city?', 'Agra', 2, 3),
                         Question('Which Dutch graphic artist–initials M C was a creator of optical illusions?',
                                  'Escher', 1, 2),
                         Question('La Giaconda is better known as what?', 'Mona Lisa', 3,
                                  2),
                         Question('How many paintings did Van Gogh sell in his lifetime?', 'One',
                                  4, 2),
                         Question(
                             'Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?',
                             'Jackson Pollock', 2, 2),
                         Question('What is the heaviest organ in the human body?', 'The Liver',
                                  4, 1),
                         Question('Who discovered penicillin?', 'Alexander Fleming', 3,
                                  1),
                         Question('Hematology is a branch of medicine involving the study of what?',
                                  'Blood', 4, 1),
                         Question('Which dung beetle was worshipped by the ancient Egyptians?', 'Scarab',
                                  4, 4)]
            for question in questions:
                question.insert()

        setUp()
        pq = Question.query.filter(Question.question == 'What year was US independence?').first().id
        param = {'quizCategory': "3",
                 'previousQuestions': [str(pq)]}
        res = self.client().post('/quizzes', json=param)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('question', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')
        tearDown()

    def test_get_categories_200(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_categories_404(self):
        def setUp():
            categories = Category.query.all()
            for category in categories:
                category.delete()
            questions = Question.query.all()
            for question in questions:
                question.delete()

        def tearDown():
            categories = [Category(1, 'Science'), Category(2, 'Art'),
                          Category(3, 'Geography'), Category(4, 'History'),
                          Category(5, 'Entertainment'), Category(6, 'Sports')]
            for category in categories:
                category.insert()
            questions = [Question('Whose autobiography is entitled ''I Know Why the Caged Bird Sings''?',
                                  'Maya Angelou', 2, 4),
                         Question('What boxer''s original name is Cassius Clay?', 'Muhammad Ali',
                                  1, 4),
                         Question('What movie earned Tom Hanks his third straight Oscar nomination, in 1996?',
                                  'Apollo 13', 4, 5),
                         Question('What actor did author Anne Rice first denounce, then praise in the role of '
                                  'her beloved Lestat?', 'Tom Cruise', 4, 5),
                         Question('What was the title of the 1990 fantasy directed by Tim Burton about a young '
                                  'man with multi-bladed appendages?', 'Edward Scissorhands', 3,
                                  5),
                         Question('Which is the only team to play in every soccer World Cup tournament?',
                                  'Brazil', 3, 6),
                         Question('Which country won the first ever soccer World Cup in 1930?',
                                  'Uruguay', 4, 6),
                         Question('Who invented Peanut Butter?', 'George Washington Carver',
                                  2, 4),
                         Question('What is the largest lake in Africa?', 'Lake Victoria',
                                  2, 3),
                         Question('In which royal palace would you find the Hall of Mirrors?',
                                  'The Palace of Versailles', 3, 3),
                         Question('The Taj Mahal is located in which Indian city?', 'Agra', 2, 3),
                         Question('Which Dutch graphic artist–initials M C was a creator of optical illusions?',
                                  'Escher', 1, 2),
                         Question('La Giaconda is better known as what?', 'Mona Lisa', 3,
                                  2),
                         Question('How many paintings did Van Gogh sell in his lifetime?', 'One',
                                  4, 2),
                         Question(
                             'Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?',
                             'Jackson Pollock', 2, 2),
                         Question('What is the heaviest organ in the human body?', 'The Liver',
                                  4, 1),
                         Question('Who discovered penicillin?', 'Alexander Fleming', 3,
                                  1),
                         Question('Hematology is a branch of medicine involving the study of what?',
                                  'Blood', 4, 1),
                         Question('Which dung beetle was worshipped by the ancient Egyptians?', 'Scarab',
                                  4, 4)]
            for question in questions:
                question.insert()

        setUp()
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('categories', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource Not Found')
        tearDown()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
