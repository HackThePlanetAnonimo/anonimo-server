import os
from flask import Flask, render_template, Response, request
import json, httplib, urllib

app = Flask(__name__)

XParseApplicationId = "8jSxdsd0pT9odu9duHaoRMouaC46SGZlglP67J4p"
XParseRESTAPIKey = "EBw6tp2t71e7MVbqWr2NpupphfQmyuh45CWy79DK"

connection = httplib.HTTPSConnection('api.parse.com', 443)
connection.connect()

@app.route('/')
def hello():
    return render_template('index.html')

# Gets all Question objects
@app.route('/get_all_questions', methods=['GET'])
def get_all_questions():
    connection.request('GET', '/1/classes/Questions/', '', {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
         })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps(result),  mimetype='application/json')

# Gets all Student objects
@app.route('/get_all_students', methods=['GET'])
def get_all_students():
    connection.request('GET', '/1/classes/Students/', '', {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
         })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps(result),  mimetype='application/json')

# Gets all questions that were asked by a particular student
@app.route('/get_all_questions_by_student_id/<student_id>', methods=['GET'])
def get_all_questions_by_student_id(student_id):
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
@app.route('/ask_a_question', methods=['POST'])
def ask_a_question():
    jsonObj = request.json
    import pdb; pdb.set_trace()
    connection.request('POST', '/1/classes/Questions/', json.dumps({
        "Student_id": str(jsonObj['Student_id']),
        "Text": str(jsonObj['Text'])
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps({'Question_id': result['objectId']}),  mimetype='application/json')


# Ability to add a student
# Requires: User_id, Name, Password
# Return: check for boolean "success". If its true, you'll also get
# the student_id inserted
@app.route('/student_sign_up', methods=['GET','POST'])
def student_sign_up():
    jsonObj = request.json
    import pdb; pdb.set_trace()
    params = urllib.urlencode({"where":json.dumps({
        "User_id": str(jsonObj['User_id']),
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
        "User_id": str(jsonObj['User_id']),
        "Password": str(jsonObj['Password']),
        "isLoggedIn": True
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps({'success': True, 'Student_id': result['objectId']}),  mimetype='application/json')

# Ability to sign in
# Requires: User_id, Password
@app.route('/student_sign_in', methods=['GET', 'POST'])
def student_sign_in():
    import pdb; pdb.set_trace()
    jsonObj = request.json
    params = urllib.urlencode({"where":json.dumps({
        "User_id": str(jsonObj['User_id']),
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
@app.route('/student_sign_out', methods=['POST'])
def student_sign_out():
    jsonObj = request.json
    studentId = jsonObj['Student_id']
    import pdb; pdb.set_trace()
    connection.request('PUT', '/1/classes/Students/'+studentId, json.dumps({
       "isLoggedIn": False
    }), {
       "X-Parse-Application-Id": XParseApplicationId,
       "X-Parse-REST-API-Key": XParseRESTAPIKey,
       "Content-Type": "application/json"
    })
    return Response(json.dumps({'success': True}),  mimetype='application/json')
# Create a model for professor
# Store username and password in the table for students
# Create a student during signup. Check if username already exists
# 


if __name__ == "__main__":
    app.run()