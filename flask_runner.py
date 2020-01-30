from flask import Flask, make_response
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, help='You must specify a username')
parser.add_argument('start_time', type=int, required=True, help='You must specify a start time as a unix timestamp')
parser.add_argument('end_time', type=int, required=True, help='You must specify an end time as a unix timestamp')

class HelloWorld(Resource):
    def get(self):
        headers = { 'Content-Type': 'text/html' }
        return make_response('This is a placeholder', 200, headers)

class PathGenerator(Resource):
    def get(self):
        args = parser.parse_args()
        return args

api.add_resource(HelloWorld, '/')
api.add_resource(PathGenerator, '/pathgenerator')

if __name__ == '__main__':
    app.run(debug=True)