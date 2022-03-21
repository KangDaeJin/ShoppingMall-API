import requests
from rest_framework.validators import ValidationError

from common.utils import BASE_IMAGE_URL
        

def validate_url(value):
    if not value.startswith(BASE_IMAGE_URL):
        raise ValidationError(detail='Enter a valid BASE_IMAGE_URL.')

    if not requests.get(value).status_code == 200:
        raise ValidationError(detail='object not found.')

    result = value.split(BASE_IMAGE_URL)
    value = result[-1]

    return value

def validate_price_difference(price, option_data):
    price_difference = option_data.get('price_difference', 0)
    if price_difference > price * 0.2:
        raise ValidationError(
            'The option price difference must be less than 20% of the product price.'
        )

def validate_sequence_ascending_order(sequences):
    sequences.sort()
    for index, value in enumerate(sequences):
        if value != (index+1):
            raise ValidationError(
                'The sequence of the images must be ascending from 1 to n.'
            )
