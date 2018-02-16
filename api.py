#!/usr/bin/env python3
#
# Serial projector REST API
#
#
import os
import time
import logging
from datetime import datetime
from projector import Projector
from vivitek import ProjectorSpec
from decorators import output_as_text
from flask import Flask, url_for, request

# Initialize logger
logging.basicConfig(filename='projectorapi.log', level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger('api')

# Use environment variable PROJECTOR_SERIAL to configure the port to use
if 'PROJECTOR_SERIAL' in os.environ:
    # this is automatically set to a suitable default in run.sh
    projector_port = os.environ['PROJECTOR_SERIAL']
else:
    # punt - fall back to a common serial port name on some Linux systems
    logger.error('PROJECTOR_SERIAL is not set in the environment')
    projector_port = '/dev/ttyS0'
logger.info('Serial port configured as: %s', projector_port)

# setup our objects
projector = Projector(projector_port)
spec = ProjectorSpec()
app = Flask(__name__)

# custom exceptions
class UnknownCommandError(ValueError):
    pass

class BadParameterError(ValueError):
    pass

class SerialError(ValueError):
    pass

# custom error handlers
@app.errorhandler(UnknownCommandError)
def unknown_command(e):
    logger.debug('UnknownCommandError handler invoked with e: %s', e)
    return "<html><head><title>Unknown Command</title></head><body><h1>404 Unknown Command</body></html>", 404

@app.errorhandler(SerialError)
def serial_port_error(e):
    logger.debug('SerialError handler invoked with e: %s', e)
    return "<html><head><title>Service Unavailable</title></head><body><h1>503 Service Unavailable</h1>"
    "<p>An error occurred while trying to access the serial port.</p></body></html>", 503

@app.errorhandler(BadParameterError)
def bad_parameter(e):
    logger.debug('BadParameterError handler invoked with e: %s', e)
    return "<html><head><title>Bad Parameter</title></head><body><h1>400 Bad Parameter</h1>"
    "<p>A required parameter was missing or out of range.</p></body></html>", 400


# Functions to actually do stuff
def do_command(command):
    try:
        logger.debug('Send command: %s', command)
        projector.send(command)
    except:
        pass

def do_query(command, delay=1):
    rv = None
    try:
        logger.debug('Send query (delay=%d): %s', delay, command)
        projector.send(command)
        time.sleep(delay)
        rv = projector.readline()
        logger.debug('Query response was: %s', rv)
    except:
        pass
    return rv


# API routes
@app.route('/api/v2/projector/')
@output_as_text
def get_projector():
    """Return a list of top-level Projector command paths."""
    resp = "Available URL paths:\n\n"
    lines = {
        'get_projector_controls': "Get list of control command nodes.", 
        'get_projector_sources': "Get list of source inputs.", 
        'get_adjustments': "Get a list of integer-based adjustments.",
        'get_settings': "Get a list of string-based settings.", 
        'get_buttons': "Get a list of remote control buttons." 
    }
    for func, desc in lines.items():
        resp += "{0}\t{1}\n".format(url_for(func), desc)
    logger.debug('get_projector(), response: %s', resp)
    return resp

@app.route('/api/v2/projector/control/')
@output_as_text
def get_projector_controls():
    """Return a list of Projector control command paths."""
    resp = "Available control URLs:\n\n"
    lines = {
        'get_projector_power': "Get projector power state.", 
        'get_projector_active_source': "Get active source (input).", 
    }
    for func, desc in lines.items():
        resp += "{0}\t{1}\n".format(url_for(func), desc)
    logger.debug('get_projector_controls(), response: %s', resp)
    return resp

@app.route('/api/v2/projector/control/power/')
@output_as_text
def get_projector_power():
    state = do_query(spec.queries['power'])
    logger.debug('get_projector_power(), response: %s', state)
    return state

@app.route('/api/v2/projector/control/power/<any(on,off):state>')
@output_as_text
def set_projector_power(state):
    if state is None or len(state) < 2:
        logger.info('Invalid power state passed to set_projector_power: %s', state)
        raise BadParameterError
    command = 'power' + state.lower()
    if command not in spec.controls:
        logger.warning('Command for %s was not found in ProjectorSpec dict!', command)
        raise BadParameterError
    do_command(spec.controls[command])
    logger.debug('set_projector_power(%s)', state)
    return 'OK'
    
@app.route('/api/v2/projector/sources/')
@output_as_text
def get_projector_sources():
    """Return a list of Projector sources (inputs)."""
    resp = 'Available sources:\n\n' + '\n'.join(spec.sources.keys())
    logger.debug('get_projector_sources(), response: %s', resp)
    return resp
    
@app.route('/api/v2/projector/control/source/')
@output_as_text
def get_projector_active_source():
    """ Return the currently active source input."""
    source = do_query(spec.queries['source'])
    logger.debug('get_projector_active_source(), response: %s', source)
    return source
        
@app.route('/api/v2/projector/control/source/<source>')
@output_as_text
def set_projector_active_source(source):
    if source is None:
        logger.info('Null source passed to set_projector_active_source')
        raise BadParameterError
    if source not in spec.sources:
        logger.warning('Unknown source %s passed to set_projector_active_source', source)
        raise UnknownCommandError
    do_command(spec.sources[source])
    logger.debug('set_projector_active_source(%s)', source)
    return 'OK'

@app.route('/api/v2/projector/adj/')
@output_as_text
def get_adjustments():
    """Return a list of Projector adjustment command paths."""
    resp = 'Available integer adjustments:\n\n'
    for adj, params in spec.adjustments.items():
        if params['type'] == 'int':
            resp += '{0}\t{1}\tRange: {2}-{3}\n'.format(adj, url_for('get_adjustment', adj=adj), params['range'][0], params['range'][1])
    logger.debug('get_adjustments(), response: %s', resp)
    return resp

@app.route('/api/v2/projector/adj/<adj>/')
@output_as_text
def get_adjustment(adj):
    if adj not in spec.adjustments or 'get' not in spec.adjustments[adj]:
        logger.warning('Unknown or unsupported adjustment %s passed to get_adjustment', adj)
        raise UnknownCommandError
    result = do_query(spec.adjustments[adj]['get'])
    logger.debug('get_adjustment(%s), response: %s', adj, result)
    return result

@app.route('/api/v2/projector/adj/<adj>/<int:param>')
@output_as_text
def set_adjustment(adj, param):
    if adj not in spec.adjustments or 'set' not in spec.adjustments[adj]:
        logger.warning('Unknown or unsupported adjustment %s passed to set_adjustment', adj)
        raise UnknownCommandError
    
    adjspec = spec.adjustments[adj]
    if adjspec['type'] == 'int':
        if param < adjspec['range'][0] or param > adjspec['range'][1]:
            logger.warning('Integer parameter to adjustment %s was out of range: %d', adj, param)
            raise BadParameterError
    else:
        logger.warning('Attempt to set an integer adjustment to non-integer setting %s', adj)
        raise BadParameterError
    
    do_command(adjspec['set'].format(param))
    logger.debug('set_adjustment(%s, %d)', adj, param)
    return 'OK'

@app.route('/api/v2/projector/set/')
@output_as_text
def get_settings():
    """Return a list of Projector setting command paths."""
    resp = 'Available settings:\n\n'
    for adj, params in spec.adjustments.items():
        if params['type'] == 'enum':
            resp += '{0}\t{1}\tOptions:\n'.format(adj, url_for('get_setting', adj=adj))
            for opt in params['labels']:
                resp += '\t{0}\t{1}\n'.format(opt, url_for('set_setting', adj=adj, param=opt))
            resp += '\n'
    logger.debug('get_settings(), response: %s', resp)
    return resp

@app.route('/api/v2/projector/set/<adj>/')
@output_as_text
def get_setting(adj):
    if adj not in spec.adjustments or 'get' not in spec.adjustments[adj]:
        logger.warning('Unknown or unsupported setting %s passed to get_setting', adj)
        raise UnknownCommandError
    result = do_query(spec.adjustments[adj]['get'])
    logger.debug('get_setting(%s), response: %s', adj, result)
    return result

@app.route('/api/v2/projector/set/<adj>/<param>')
@output_as_text
def set_setting(adj, param):
    if adj not in spec.adjustments or 'set' not in spec.adjustments[adj]:
        logger.warning('Unknown or unsupported setting %s passed to set_setting', adj)
        raise UnknownCommandError
    
    adjspec = spec.adjustments[adj]
    if adjspec['type'] == 'enum':
        if param not in adjspec['labels']:
            logger.warning('Parameter to setting %s was unknown or unsupported: %s', adj, param)
            raise BadParameterError
    else:
        logger.warning('Attempt to pass string setting to integer adjustment %s', adj)
        raise BadParameterError
    
    do_command(adjspec['set'].format(param))
    logger.debug('set_adjustment(%s, %s)', adj, param)
    return 'OK'

@app.route('/api/v2/projector/button/')
@output_as_text
def get_buttons():
    """Return a list of remote control buttons."""
    resp = "Available buttons:\n\n"
    for name in sorted(spec.buttons.keys()):
        resp += '{0}\t{1}\n'.format(name, url_for('push_button', name=name))
    logger.debug('get_buttons(), response: %s', resp)
    return resp

@app.route('/api/v2/projector/button/<name>')
@output_as_text
def push_button(name):
    if name not in spec.buttons:
        logger.warning('Unknown button %s passed to push_button', name)
        raise UnknownCommandError
    do_command(spec.buttons[name])
    logger.debug('push_button(%s)', name)
    return 'OK'


# start the server if we were invoked directly
if __name__ == '__main__':
    logger.info("Launching API at %s", datetime.now().isoformat('T'))
    print('Application started. Press Ctrl+C to exit.')
    app.run(host='0.0.0.0')
