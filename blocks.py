import time


class Executable:
    def execute(self, controller):
        pass


class Sequence(Executable):
    def __init__(self, repeat, steps):
        self.repeat = repeat
        self.steps = steps

    @staticmethod
    def decode(data):
        if data['type'] != "sequence":
            return

        repeat = data['repeat']
        steps = []

        for step in data['steps']:
            type = step['type']

            if type == 'delay':
                steps.append(Delay.decode(step))
            elif type == 'actions':
                steps.append(Actions.decode(step))

        return Sequence(repeat, steps)

    def execute(self, controller):
        for i in range(self.repeat):
            for step in self.steps:
                step.execute(controller)


class Delay(Executable):
    def __init__(self, delay):
        self.delay = delay

    @staticmethod
    def decode(data):
        return Delay(float(data['delay']))

    def execute(self, controller):
        time.sleep(self.delay)


class Actions(Executable):
    def __init__(self, actions):
        self.actions = actions

    @staticmethod
    def decode(data):
        actions = []

        for action in data['actions']:
            type = action['type']

            if type == 'turn':
                actions.append(Turn.decode(action))

        return Actions(actions)

    def execute(self, controller):
        positions = []
        states = []
        for action in self.actions:
            positions.append(action.position)
            states.append(action.state)

        controller.set_states(positions, states)


class Turn:
    def __init__(self, position, state):
        self.position = position
        self.state = state

    @staticmethod
    def decode(data):
        position = list(map(int, data['position'].split(",")))
        state = data['state']
        return Turn(position, int(state))
