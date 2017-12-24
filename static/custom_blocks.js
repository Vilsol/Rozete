Blockly.Blocks['sequence'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Sequence");
        this.appendDummyInput()
            .appendField("Repeat")
            .appendField(new Blockly.FieldNumber(10, 1, 100), "REPEAT")
            .appendField("times");
        this.appendStatementInput("STEPS")
            .setCheck("STEP");
        this.setColour(330);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

Blockly.Blocks['delay'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Delay")
            .appendField(new Blockly.FieldNumber(1, 0, 60, 0.01), "DELAY")
            .appendField("second(s)");
        this.setPreviousStatement(true, "STEP");
        this.setNextStatement(true, "STEP");
        this.setColour(120);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

Blockly.Blocks['actions'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Actions");
        this.appendStatementInput("ACTIONS")
            .setCheck("ACTION");
        this.setPreviousStatement(true, "STEP");
        this.setNextStatement(true, "STEP");
        this.setColour(120);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};

Blockly.Blocks['state'] = {
    init: function () {
        this.appendDummyInput()
            .appendField("Turn")
            .appendField(new Blockly.FieldDropdown(coordinates), "POSITION")
            .appendField(new Blockly.FieldDropdown([["ON", "1"], ["OFF", "0"]]), "STATE");
        this.setPreviousStatement(true, "ACTION");
        this.setNextStatement(true, "ACTION");
        this.setColour(230);
        this.setTooltip("");
        this.setHelpUrl("");
    }
};