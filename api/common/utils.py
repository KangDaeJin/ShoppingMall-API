from rest_framework.views import exception_handler
from user.models import User

def get_result_message(code=200, message='success', data=None):
    result = {
        'code': code,
        'message': message, 
    }
    if data:
        result['data'] = data
    return result

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = {'code': response.status_code}
    if isinstance(response.data, dict):
        if 'detail' in response.data:
            data['message'] = response.data['detail']
        else:
            data['message'] = response.data
    elif isinstance(response.data, list):
        data['message'] = response.data
    
    response.data = data    
    return response
