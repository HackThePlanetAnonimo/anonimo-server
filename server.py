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


@app.route('/add_a_student', methods=['POST'])
def add_a_student():
    jsonObj = request.json
    connection.request('POST', '/1/classes/Students/', json.dumps({
        "Name": str(jsonObj['Name'])
    }), {
           "X-Parse-Application-Id": XParseApplicationId,
           "X-Parse-REST-API-Key": XParseRESTAPIKey,
    })
    result = json.loads(connection.getresponse().read())
    return Response(json.dumps({'Student_id': result['objectId']}),  mimetype='application/json')



if __name__ == "__main__":
    app.run()