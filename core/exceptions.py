
# custom exceptions.py
from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidUserDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid data provided for user creation.'
    default_code = 'invalid_user_data'
