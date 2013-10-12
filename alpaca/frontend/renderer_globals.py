from pyramid.threadlocal import get_current_request

def handler(event):
    request = get_current_request()
    event['local_time'] = lambda date: (
        date.astimezone(request.timezone)
    )
