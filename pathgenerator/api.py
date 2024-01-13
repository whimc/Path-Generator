from flask import Flask, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import json
import os
from server.markdown_to_html import toHTML

import pathgenerator.runner as runner

app = Flask(__name__)
CORS(app)
api = Api(app, prefix='/path-generator')

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, help='You must specify a username', location='args')
parser.add_argument('start_time', type=int, required=True, help='You must specify a start time as a unix timestamp', location='args')
parser.add_argument('end_time', type=int, required=True, help='You must specify an end time as a unix timestamp', location='args')
parser.add_argument('gen_empty', type=bool, required=False, default=False, location='args')

def get_message(success, message):
    return json.dumps({'success': success, 'message': message})

class Default(Resource):
    def get(self):
        headers = { 'Content-Type': 'text/html' }
        return make_response(toHTML(os.path.join('server', 'lander_page.md')), 200, headers)


class PathGenerator(Resource):
    def get(self):
        args = parser.parse_args()

        username = args.get('username')
        start_time = args.get('start_time')
        end_time = args.get('end_time')
        gen_empty = args.get('gen_empty') or False

        links = runner.get_path_links(username, start_time, end_time, gen_empty=gen_empty)

        return make_response({'success': True, 'links': links or []})

api.add_resource(Default, '/')
api.add_resource(PathGenerator, '/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
