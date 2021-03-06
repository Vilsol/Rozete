from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO

from blocks import Sequence

from threading import Thread

import requests
import json
import random
import signal

config = json.load(open("server.json"))

live_config = {
    "sequence_enabled": False,
    "lights_on": True
}


class Controller:
    def __init__(self, puppets, layout, socket):
        self.puppets = puppets
        self.layout = layout
        self.socket = socket

    @staticmethod
    def send_request(endpoint, data, headers, override=False):
        if override or live_config["sequence_enabled"]:
            try:
                requests.put(endpoint, data=data, headers=headers).json()
            except:
                print("Failed to PUT:", endpoint)

    def set_state(self, row, col, state, override=False):
        compound = self.layout[row][col]

        if compound is None:
            return

        self.socket.emit("turn", json.dumps({"pos": [row, col], "state": state}))

        puppet = self.puppets[compound[0]]
        switch = compound[1]

        endpoint = "http://" + puppet['remote'] + "/v1/switch/" + str(switch)
        data = json.dumps({"state": state})
        headers = {'rozete-token': puppet['token']}

        Controller.send_request(endpoint, data, headers, override)

    def set_states(self, positions, states, override=False):
        results = {}

        for i in range(len(positions)):
            compound = self.layout[positions[i][0]][positions[i][1]]

            if compound is None:
                continue

            self.socket.emit("turn", json.dumps({"pos": positions[i], "state": states[i]}))

            puppet = self.puppets[compound[0]]
            switch = compound[1]

            if compound[0] not in results:
                results[compound[0]] = {'switches': [], 'states': [], 'puppet': puppet}

            results[compound[0]]['switches'].append(str(switch))
            results[compound[0]]['states'].append(states[i])

        threads = []

        for i in results:
            result = results[i]

            endpoint = "http://" + result['puppet']['remote'] + "/v1/switches/" + (",".join(result['switches']))
            data = json.dumps({"states": result['states']})
            headers = {'rozete-token': result['puppet']['token']}

            thread = Thread(target=Controller.send_request, args=(endpoint, data, headers, override,))
            thread.start()

        for i in threads:
            i.join()

    def all_turn(self, state):
        positions = []
        states = []
        for row in range(len(self.layout)):
            for col in range(len(self.layout[row])):
                positions.append([row, col])
                states.append(state)

        self.set_states(positions, states, True)

    def all_on(self):
        self.all_turn(1)

    def all_off(self):
        self.all_turn(0)

    def highlight(self, id):
        self.socket.emit("highlight", id)


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
            if sequence.alone:
                return [sequence]
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

    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='threading')

    controller = Controller(config['puppets'], config['layout'], socketio)


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


    @app.route('/layout')
    def layout():
        result = {}
        for row in range(len(config['layout'])):
            result[row] = {}
            for col in range(len(config['layout'][row])):
                if config['layout'][row][col] is not None:
                    result[row][col] = 1
                else:
                    result[row][col] = 0

        return json.dumps({"success": True, "data": result})


    @app.route('/live_config')
    def get_live_config():
        return json.dumps({"success": True, "data": live_config})


    @socketio.on('live_config')
    def handle_message(message):
        global live_config
        live_config = message

        if not live_config["sequence_enabled"]:
            if live_config["lights_on"]:
                controller.all_on()
            else:
                controller.all_off()


    def signal_term_handler(signal, frame):
        controller.all_off()
        exit(0)


    signal.signal(signal.SIGTERM, signal_term_handler)

    thread = Thread(target=lights_loop, args=(controller,))
    thread.start()

    controller.all_on()

    try:
        socketio.run(app, host='0.0.0.0', port='8080', log_output=False)

        thread.join()
    except Exception as e:
        pass
    finally:
        controller.all_off()
