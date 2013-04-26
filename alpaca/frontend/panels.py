def big_message(context, request, header, message):
    return {
        'header': header,
        'message': message,
    }
