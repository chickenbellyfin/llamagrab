from sanic import Request

def if_htmx(value):
    return value if Request.get_current().headers.get('hx-request') else None
    