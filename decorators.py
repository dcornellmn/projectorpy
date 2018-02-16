import functools
from flask import make_response

def output_as_json(f):
    """Generate a JSON response from a a Python dictionary."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # invoke the wrapped function
        rv = f(*args, **kwargs)

        # the wrapped function can return the dictionary alone,
        # or can also include a status code and/or headers.
        # here we separate all these items
        status = None
        headers = None
        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status, (dict, list)):
            headers, status = status, None

        # generate the JSON response
        rv = jsonify(rv)
        if status is not None:
            rv.status_code = status
        if headers is not None:
            rv.headers.extend(headers)
        return rv
    return wrapped

def output_as_text(f):
    """Generate a text/plain response from a string."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # invoke the wrapped function
        rv = f(*args, **kwargs)

        # the wrapped function can return the string alone,
        # or can also include a status code and/or headers.
        # here we separate all these items
        status = None
        headers = None
        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status, (dict, list)):
            headers, status = status, None

        # generate the text response
        rv = str(rv) + '\n'
        rv = make_response(rv)
        if status is not None:
            rv.status_code = status
        if headers is not None:
            rv.headers.extend(headers)
        rv.mimetype = 'text/plain'
        return rv
    return wrapped

