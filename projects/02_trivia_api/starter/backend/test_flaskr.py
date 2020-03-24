import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:19970518@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            "question": "Who is ME?",
            "answer": "Tailin Lyu",
            "category": 4,
            "difficulty": 3
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
    #Test for getting all categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    #Test for getting questions in page
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertFalse(data['current_category'])
        self.assertEqual(len(data['questions']),10)
    #Test for deleting questions by ID
    def test_delete_questions(self):
        length = len(Question.query.all())
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        self.assertEqual(data['deleted'],5)
        self.assertEqual(data['total_questions'],length-1)
        self.assertTrue(data['success'])
    #Test for deleting questions by not existed ID

    #Test for Posting a new question
    def test_create_question(self):
        res = self.client().post('/questions',json=self.new_question)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['created'])
    #Test for Posting a new question for incorrect api
    def test_405_create_question(self):
        res = self.client().post('/questions/100',json=self.new_question)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 405)
    #Test for Getting questions based on category
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['current_category'],'Science')
    #Test for Getting questions based on not found category
    
    def test_404_get_questions_by_category(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 404)
    def test_get_questions_by_search_term(self):
        res = self.client().get('/questions?page=1&search_term=movie')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_questions(self):
        res = self.client().delete('/questions/20')
        self.assertEqual(res.status_code, 200)
    def test_404_delete_questions(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        #print(res.get_json())
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
    def test_create_questions(self):
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'category': 1,
            'difficulty': 1,
        }
        res = self.client().post('/questions', json=new_question)
        self.assertEqual(res.status_code, 200)

    def test_422_create_questions(self):
        invalid_question = {
            'question': 'invalid question',
            'answer': 'invalid answer',
            'category': 'Not integer',
            'difficulty': 'Not integer',
        }
        res = self.client().post('/questions', json=invalid_question)
        self.assertEqual(res.status_code, 422)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))
    
    def test_quizzes(self):
        body = {
            'previous_questions': [ 2, 4 ],
            'quiz_category': {"type": "Science", "id": 1},
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()