from flask import Flask, make_response
from flask_restful import Resource, Api, reqparse
import json

import runner

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, help='You must specify a username')
parser.add_argument('start_time', type=int, required=True, help='You must specify a start time as a unix timestamp')
parser.add_argument('end_time', type=int, required=True, help='You must specify an end time as a unix timestamp')

def get_message(success, message):
    return json.dumps({'success': success, 'message': message})

class Default(Resource):
    def get(self):
        headers = { 'Content-Type': 'text/html' }
        return make_response('This is a placeholder', 200, headers)

class PathGenerator(Resource):
    def get(self):
        args = parser.parse_args()

        username = args.get('username')
        start_time = args.get('start_time')
        end_time = args.get('end_time')

        links = runner.get_path_links(username, start_time, end_time)

        return {'success': True, 'links': links}

api.add_resource(Default, '/')
api.add_resource(PathGenerator, '/pathgenerator')

if __name__ == '__main__':
    app.run(debug=True)