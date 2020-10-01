import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        postgres_username = os.getenv('POSTGRES_USERNAME')
        postgres_password = os.getenv('POSTGRES_PASSWORD')
        self.database_path = f"postgresql://{postgres_username}:{postgres_password}@localhost:5432/{self.database_name}"

        setup_db(self.app, self.database_path)
        self.new_question = {
            'question': 'efwqf',
            'answer': 'wqfe',
            'category': "2",
            'difficulty': 2
        }

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

    def test_get_paginated_questions(self):
        """Test returning pages """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue('current_category' in data.keys())

    def test_questions_404(self):
        """Test returning a 404 error code when requesting non existed page """
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        """Test creating a new question"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_question_id_405(self):
        """Test return a 405 error code for not allowed method on questions/question_id """
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_question_search_with_results(self):
        """Test getting a list of matched questions thourgh search endpoint"""
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'title'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 2)

    def test_question_search_without_results(self):
        """Testing getting no results for the search """
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'efasdgderdav'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_question_delete(self):
        """Test deleting questions"""
        res = self.client().delete('/questions/20')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 20).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 20)
        self.assertEqual(question, None)

    def test_question_delete_422(self):
        """Test raising a 422 error"""
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_quiz_play(self):
        """test playing the quiz """
        res = self.client().post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {'id': '1'}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_quiz_no_questions(self):
        """Test playing the quiz with no questions remaining in the requested category"""
        res = self.client().post('/quizzes', json={
            "previous_questions": [20, 21, 22, 7],
            "quiz_category": {'id': '1'}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['question'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
