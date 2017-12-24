Blockly.JavaScript['sequence'] = function (block) {
    var steps = Blockly.JavaScript.statementToCode(block, 'STEPS');

    steps = steps.substr(0, steps.length - 1);

    return '{"type": "sequence", "repeat": ' + block.getFieldValue('REPEAT') + ', "steps": [' + steps + ']},';
};

Blockly.JavaScript['delay'] = function (block) {
    return '{"type": "delay", "delay": ' + block.getFieldValue('DELAY') + '},';
};

Blockly.JavaScript['actions'] = function (block) {
    var actions = Blockly.JavaScript.statementToCode(block, 'ACTIONS');

    actions = actions.substr(0, actions.length - 1);

    return '{"type": "actions", "actions": [' + actions + ']},';
};

Blockly.JavaScript['state'] = function (block) {
    return '{"type": "turn", "position": "' + block.getFieldValue('POSITION') + '", "state": ' + block.getFieldValue('STATE') + '},';
};