from RPi import GPIO

from flask import Flask, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonify

from functools import wraps

import json

config = json.load(open("puppet.json"))


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("rozete-token")
        if not token or config['token'] != token:
            return jsonify({"success": False, "error": "auth token invalid"})
        return f(*args, **kwargs)

    return decorated


class Pins(Resource):
    @staticmethod
    @requires_auth
    def get():
        pins = {}

        for i in range(len(config['pins'])):
            pins[i] = config['pins'][i]

        return jsonify({"success:": True, "data": pins})


class Switches(Resource):
    @staticmethod
    @requires_auth
    def get():
        pins = {}

        for i in range(len(config['pins'])):
            pins[i] = GPIO.input(config['pins'][i])

        return jsonify({"success:": True, "data": pins})


class Switch(Resource):
    @staticmethod
    @requires_auth
    def get(switch):
        return jsonify({"success": True, "data": GPIO.input(config['pins'][int(switch)])})

    @staticmethod
    @requires_auth
    def put(switch):
        state = 0

        try:
            state = json.loads(request.data.decode())['state']
        except Exception as e:
            print(e)

        GPIO.output(config['pins'][int(switch)], state)

        return jsonify({"success": True, "data": GPIO.input(config['pins'][int(switch)])})


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)

    for pin in config['pins']:
        GPIO.setup(pin, GPIO.OUT)

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Pins, '/v1/pins')
    api.add_resource(Switches, '/v1/switches')
    api.add_resource(Switch, '/v1/switch/<switch>')

    app.run(host='0.0.0.0', port='8080')
