import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Define Paginate Questions

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        return questions[start:end]
    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    # Below is the CORS setup
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        cats = {}
        for cat in categories:
            cats[cat.id] = cat.type
        return jsonify(
            {
                'success': True,
                'categories': cats
            }
        )

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()
        questions_selection = paginate_questions(request, questions)
        cats = {}
        current_cats = None
        for cat in categories:
            cats[cat.id] = cat.type
        return jsonify(
            {
                'success': True,
                'questions': questions_selection,
                'total_questions': len(questions),
                'current_category': current_cats,
                "categories": cats
            }
        )
    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if question == None:
            abort(404)
        question.delete()
        questions = Question.query.all()
        questions_selection = paginate_questions(request, questions)
        return jsonify({
            'success': True,
            'deleted': question_id,
            'questions': questions_selection,
            'total_questions': len(questions)
        })

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body['question']
        new_answer = body['answer']
        new_category = body['category']
        new_difficulty = body['difficulty']
        try:
            question = Question(
                new_question,
                new_answer,
                new_category,
                new_difficulty
            )
            question.insert()
            questions = Question.query.all()
            questions_selection = paginate_questions(request, questions)
            return jsonify(
                {
                    'success': True,
                    'created': question.id,
                    'total_questions': len(questions),
                    'questions': questions_selection
                }
            )
        except:
            abort(422)

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/searchQuestions', methods=['POST'])
    def search_questions():
      search_term = request.get_json()['searchTerm']
      print(search_term)
      cats = {}
      categories = Category.query.all()
      for cat in categories:
        cats[cat.id] = cat.type
      current_cats = {}
      search_result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      questions_selection = paginate_questions(request, search_result)
      for result in search_result:
        current_cats[result.category] = cats[result.category]
      print(current_cats)
      return jsonify(
        {
          'success': True,
          'questions': questions_selection,
          'total_questions': len(search_result),
          'current_category': current_cats,
          "categories": cats
        }
      )
    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
      questions = Question.query.filter_by(category=category_id).all()
      questions_selection = paginate_questions(request,questions)
      current_category = Category.query.filter_by(id=category_id).first().type
      return jsonify(
        {
          'success':True,
          'questions': questions_selection,
          'total_questions': len(questions),
          'current_category': current_category
        }
      )
      
    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['Post'])
    def play_quizzes():
      body = request.get_json()
      quiz_category = body['quiz_category']
      previous_questions = body['previous_questions']
      if(quiz_category.get('id') == 0):
        category_questions = Question.query.all()
      else:
        category_questions = Question.query.filter_by(category=quiz_category['id']).all()
      questions_id = [ques.id for ques in category_questions]
      available_questions = []
      for cat_que in questions_id:
        if not cat_que in previous_questions:
          available_questions.append(cat_que)
      print('available questions: ', available_questions)
      if(len(available_questions) < 1):
        current_question = None
      else:
        ran_int = random.randint(0,len(available_questions)-1)
        current_question = available_questions[ran_int]
        previous_questions.append(current_question)
      print('current questions: ',current_question) 
      return jsonify(
        {
          'success': True,
          'previousQuestions': previous_questions,
          'question': None if current_question==None else Question.query.filter_by(id = current_question).first().format()
        }
      )

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
      })
    @app.errorhandler(422)
    def unprocessable_entity(error):
      return jsonify(
        {
          "success": False,
          "error": 422,
          "message": "resource is an unprocessable_entity"
        }
      )


    return app
