import os
from flask import Flask, render_template, Response, request
import json, httplib, urllib

app = Flask(__name__)

XParseApplicationId = "8jSxdsd0pT9odu9duHaoRMouaC46SGZlglP67J4p"
XParseRESTAPIKey = "EBw6tp2t71e7MVbqWr2NpupphfQmyuh45CWy79DK"

@app.route('/')
def hello():
    return render_template('index.html')

# Gets all Question objects
@app.route('/get_all_questions', methods=['GET'])
def get_all_questions():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/classes/Questions/', '', {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
         })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps(result),  mimetype='application/json')

# Gets all Student objects
@app.route('/get_all_students', methods=['GET'])
def get_all_students():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/classes/Students/', '', {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
         })
    result = json.loads(connection.getresponse().read())
    resp = Response(json.dumps(result),  mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Gets all questions that were asked by a particular student
@app.route('/get_all_questions_by_student_id/<student_id>', methods=['GET'])
def get_all_questions_by_student_id(student_id):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    params = urllib.urlencode({"where":json.dumps({
        "Student_id": student_id,
    })})
    connection.request('GET', '/1/classes/Questions/?%s' % params, '', {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
         })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps(result),  mimetype='application/json')

# Ability to ask a question

# TODO: First check if student is logged in
# Or have a route that just tells if logged in or not and prevent the 
# frontend from making a call if not logged in
# {"Student_id": "kV2kIEKENH", "Text": "I am thirsty"}
@app.route('/ask_a_question', methods=['POST'])
def ask_a_question():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    connection.request('POST', '/1/classes/Questions/', json.dumps({
        "Student_id": str(jsonObj['Student_id']),
        "Text": str(jsonObj['Text']),
        "Status": "unanswered",
        "Votes": 0
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps({'Question_id': result['objectId']}),  mimetype='application/json')


# Ability to add a student
# Requires: Email, Name, Password
# Return: check for boolean "success". If its true, you'll also get
# the student_id inserted
# {"Email": "squatle@uwaterloo.ca", "Password": "waterwater", "Name": "Squartle"}
@app.route('/student_sign_up', methods=['GET','POST'])
def student_sign_up():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    params = urllib.urlencode({"where":json.dumps({
        "Email": str(jsonObj['Email']),
    })})

    # Check if User_id already taken
    connection.request('GET', '/1/classes/Students/?%s' % params, '', {
        "X-Parse-Application-Id": XParseApplicationId,
        "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    # userid already exists. Signup fails
    if len(result['results']) > 0:
        return Response(json.dumps({'success': False}),  mimetype='application/json')

    connection.request('POST', '/1/classes/Students/', json.dumps({
        "Name": str(jsonObj['Name']),
        "Email": str(jsonObj['Email']),
        "Password": str(jsonObj['Password']),
        "isLoggedIn": True
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps({'success': True, 'Student_id': result['objectId']}),  mimetype='application/json')

# Ability to sign in
# Requires: Email, Password
# {"Email": "pikachu@uwaterloo.ca", "Password": "iamfat"}
@app.route('/student_sign_in', methods=['GET', 'POST'])
def student_sign_in():
    import pdb; pdb.set_trace()
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    params = urllib.urlencode({"where":json.dumps({
        "Email": str(jsonObj['Email']),
        "Password": str(jsonObj['Password'])
    })})
    connection.request('GET', '/1/classes/Students/?%s' % params, '', {
        "X-Parse-Application-Id": XParseApplicationId,
        "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    results = json.loads(connection.getresponse().read())['results']

    # Invalid credentials
    if len(results) == 0:
        return Response(json.dumps({'success': False}),  mimetype='application/json')

    studentId = results[0]['objectId']
    connection.request('PUT', '/1/classes/Students/'+studentId, json.dumps({
       "isLoggedIn": True
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json')
    # Given User_id and Password, fetch a student. If you cant, invalid credentials.
    # Else, using the ObjectId, PUT to update isLoggedIn

# Expects: Student_id
# {"Student_id": "L5cfAtIG6y"}
@app.route('/student_sign_out', methods=['POST'])
def student_sign_out():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    studentId = jsonObj['Student_id']
    connection.request('PUT', '/1/classes/Students/'+studentId, json.dumps({
       "isLoggedIn": False
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json')  

# ------------- Professors -------------------------------------------

# Ability to add a professor
# Requires: Email, Name, Password
# Return: check for boolean "success".
# {"Email": "ash@uwaterloo.ca", "Password": "ketchup", "Name": "ash"}
@app.route('/professor_sign_up', methods=['GET','POST'])
def professor_sign_up():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    params = urllib.urlencode({"where":json.dumps({
        "Email": str(jsonObj['Email']),
    })})

    # Check if Email already taken
    connection.request('GET', '/1/classes/Professors/?%s' % params, '', {
        "X-Parse-Application-Id": XParseApplicationId,
        "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    # Email already exists. Signup fails
    if len(result['results']) > 0:
        resp = Response(json.dumps({'success': False}),  mimetype='application/json')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    connection.request('POST', '/1/classes/Professors/', json.dumps({
        "Name": str(jsonObj['Name']),
        "Email": str(jsonObj['Email']),
        "Password": str(jsonObj['Password']),
        "isLoggedIn": True
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    resp = Response(json.dumps({'success': True, 'Professor_id': result['objectId']}),  mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Ability to sign in
# Requires: Email, Password
@app.route('/professor_sign_in', methods=['GET', 'POST'])
def professor_sign_in():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    params = urllib.urlencode({"where":json.dumps({
        "Email": str(jsonObj['Email']),
        "Password": str(jsonObj['Password'])
    })})
    connection.request('GET', '/1/classes/Professors/?%s' % params, '', {
        "X-Parse-Application-Id": XParseApplicationId,
        "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    results = json.loads(connection.getresponse().read())['results']

    # Invalid credentials
    if len(results) == 0:
        return Response(json.dumps({'success': False}),  mimetype='application/json')

    professorId = results[0]['objectId']
    connection.request('PUT', '/1/classes/Professors/'+professorId, json.dumps({
       "isLoggedIn": True
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json')  

# Expects: Professor_id (Professor's objectId)
@app.route('/professor_sign_out', methods=['POST'])
def professor_sign_out():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    professorId = jsonObj['Professor_id']
    connection.request('PUT', '/1/classes/Professors/'+professorId, json.dumps({
       "isLoggedIn": False
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json') 

# Create a model for professor: Name, email, Password, isLoggedIn
@app.route('/get_all_professors', methods=['GET'])
def get_all_professors():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/classes/Professors/', '', {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
         })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps(result),  mimetype='application/json')

# expects: Question_id
# modifies: Status field of Question model
# {"Question_id": "koRfJ5lj2W"}
@app.route('/answer_a_question', methods=['POST'])
def answer_a_question():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    questionId = jsonObj['Question_id']
    connection.request('PUT', '/1/classes/Questions/'+questionId, json.dumps({
       "Status": "answered"
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json')  

# expects: Question_id
# modifies: Votes field of Question model
# {"Question_id": "koRfJ5lj2W"}
@app.route('/vote_a_question', methods=['POST'])
def vote_a_question():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    questionId = jsonObj['Question_id']
    connection.request('PUT', '/1/classes/Questions/'+questionId, json.dumps({
        "Votes": {
            "__op": "Increment",
            "amount": 1
        }
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json') 

# {"Professor_id": "ebS7BImXgB", "Student_ids": "kV2kIEKENH,L5cfAtIG6y"}
# bunch of student ids separated by comma
@app.route('/setup_a_lecture', methods=['POST'])
def setup_a_lecture():
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    jsonObj = request.json
    professorId = jsonObj['Professor_id']
    
    connection.request('POST', '/1/classes/Lectures/', json.dumps({
        "Professor_Id": str(jsonObj['Professor_id']),
        "Student_Ids": str(jsonObj['Student_ids'])
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps({'success': True, 'Lecture_id': result['objectId']}),  mimetype='application/json')


if __name__ == "__main__":
    app.run()