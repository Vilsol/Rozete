from flask import Flask, request, send_from_directory

from blocks import Sequence

import requests
import json
import ezthread
import random

config = json.load(open("server.json"))


class Controller:
    def __init__(self, puppets, layout):
        self.puppets = puppets
        self.layout = layout

    def set_state(self, row, col, state):
        compound = self.layout[row][col]

        if compound is None:
            return

        puppet = self.puppets[compound[0]]
        switch = compound[1]

        endpoint = "http://" + puppet['remote'] + "/v1/switch/" + str(switch)
        data = json.dumps({"state": state})
        headers = {'rozete-token': puppet['token']}

        requests.put(endpoint, data=data, headers=headers).json()

    def set_states(self, positions, states):
        results = {}

        for i in range(len(positions)):
            compound = self.layout[positions[i][0]][positions[i][1]]

            if compound is None:
                continue

            puppet = self.puppets[compound[0]]
            switch = compound[1]

            if compound[0] not in results:
                results[compound[0]] = {'switches': [], 'states': [], 'puppet': puppet}

            results[compound[0]]['switches'].append(str(switch))
            results[compound[0]]['states'].append(states[i])

        for i in results:
            result = results[i]

            endpoint = "http://" + result['puppet']['remote'] + "/v1/switches/" + (",".join(result['switches']))
            data = json.dumps({"states": result['states']})
            headers = {'rozete-token': result['puppet']['token']}

            requests.put(endpoint, data=data, headers=headers).json()


def get_switches(puppets):
    switches = []

    for puppet in range(len(puppets)):
        for switch in puppets[puppet]['switches']:
            switches.append([puppet, switch])

    return switches


def validate_layout(layout, switches):
    for row in layout:
        for col in row:
            if col is not None:
                if col not in switches:
                    return False

    return True


def get_coordinates(layout):
    coordinates = []

    for row in range(len(layout)):
        for col in range(len(layout[row])):
            if layout[row][col] is not None:
                coordinates.append([row, col])

    return coordinates


def reload_sequences():
    with open("sequence.json", "r+") as f:
        data = json.loads(f.read())

    sequences = []

    for raw in data:
        sequence = Sequence.decode(raw)
        if sequence is not None:
            sequences.append(sequence)

    return sequences


def lights_loop(controller):
    try:
        while True:
            sequences = reload_sequences()
            for i in range(len(sequences)):
                random.shuffle(sequences)
                sequence = sequences.pop()
                sequence.execute(controller)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    switches = get_switches(config['puppets'])

    if not validate_layout(config['layout'], switches):
        print("Invalid Layout")
        exit(1)

    controller = Controller(config['puppets'], config['layout'])

    app = Flask(__name__)


    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)


    @app.route('/save', methods=["POST"])
    def save():
        data = json.loads(request.data.decode())

        with open("sequence.json", "w+") as f:
            f.write(data['json'])

        with open("sequence.xml", "w+") as f:
            f.write(data['xml'])

        return json.dumps({"success": True})


    @app.route('/coordinates')
    def coordinates():
        result = []
        coordinates = get_coordinates(config['layout'])

        for i in range(len(coordinates)):
            result.append([str(coordinates[i][0]) + " : " + str(coordinates[i][1]),
                           str(coordinates[i][0]) + "," + str(coordinates[i][1])])

        return "var coordinates = " + json.dumps(result)


    @app.route('/xml')
    def xml():
        with open("sequence.xml", "r+") as f:
            return f.read()


    pool = ezthread.EzPool()
    pool.submit(lights_loop, controller)

    app.run(host='0.0.0.0', port='8080')

    pool.kill()
