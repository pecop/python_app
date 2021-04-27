'use strict';

eel.expose(logger)
function logger(message) {

    const loggerNode = document.getElementById('logger')
    loggerNode.textContent += message + '\n'

}
