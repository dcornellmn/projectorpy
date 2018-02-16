#!/usr/bin/env python3
#
# Implements projector command specification at:
# http://www.vivitek.eu/Files/ControlProtocols/Projection%20Display%20Serial%20Interface%20Spesification%20v1.9.pdf
#

class ProjectorSpec:
    """ Contains definitions and utility methods to work with a specific projector protocol """
    
    # TODO: Generify this class
    controls = {
        'poweron': '~PN\r',
        'poweroff': '~PF\r',
        'autoimage': '~AI\r',
        'newlamp': '~RL\r'
    }
    sources = {
        'RGB': '~SR\r',
        'RGB2': '~SG\r',
        'DVI': '~SD\r',
        'HDMI': '~SH\r',
        #'HDMI2': '~SI\r',
        'Video': '~SV\r',
        'S-Video': '~SS\r',
        'Component': '~SY\r',
        'Wireless': '~SW\r'
    }
    queries = {
        'version': '~qV\r',
        'power': '~qP\r',
        'source': '~qS\r',
        'lamphours': '~qL\r',
        'volume': '~qM\r',
        'frozen': '~qZ\r',
        'muted': '~qU\r',
        'blanked': '~qK\r'
    }
    adjustments = {
        'brightness': { 'get': '~qB\r', 'set': '~sB{}\r', 'type':'int', 'range':(0,100) },
        'contrast': { 'get': '~qC\r', 'set': '~sC{}\r', 'type':'int', 'range':(0,100) },
        'color': { 'get': '~qR\r', 'set': '~sR{}\r', 'type':'int', 'range':(0,100) },
        'tint': { 'get': '~qN\r', 'set': '~sN{}\r', 'type':'int', 'range':(0,100) },
        'scaling': { 'get': '~qA\r', 'set': '~sA{}\r', 'type':'enum', 'range':(0,4), 'labels': ['Fill', '4:3', '16:9', 'LetterBox', 'Native'] },
        'colortemp': { 'get': '~qT\r', 'set': '~sT{}\r', 'type':'enum', 'range':(0,2), 'labels': ['6500', '9300', '10500'] },
        'projectionmode': { 'get': '~qJ\r', 'set': '~sJ{}\r', 'type':'enum', 'range':(0,3), 'labels': ['Front', 'Rear', 'Rear+Ceiling', 'Ceiling'] },
        'sharpness': { 'get': '~qH\r', 'set': '~sH{}\r', 'type':'int', 'range':(0,31) }
    }
    buttons = { 
        'up': '~rU\r',
        'down': '~rD\r',
        'left': '~rL\r',
        'right': '~rR\r',
        'power': '~rP\r',
        'power2': '~rP\r~rP\r',
        'exit': '~rE\r',
        'input': '~rI\r',
        'auto': '~rA\r',
        'keystone+': '~rK\r',
        'keystone-': '~rJ\r',
        'menu': '~rM\r',
        'status': '~rS\r',
        'mute': '~rT\r',
        'zoom+': '~rZ\r',
        'zoom-': '~rY\r',
        'blank': '~rB\r',
        'freeze': '~rF\r',
        'volume+': '~rV\r',
        'volume-': '~rW\r',
        'enter': '~rN\r'
    }
