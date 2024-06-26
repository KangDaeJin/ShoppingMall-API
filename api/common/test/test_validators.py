from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField, IntegerField
from rest_framework.test import APITestCase

from .test_cases import FunctionTestCase
from .factories import TemporaryImageFactory
from ..models import TemporaryImage
from ..validators import validate_all_required_fields_included, validate_image_url
from ..utils import BASE_IMAGE_URL


class ValidateRequireDataInPartialUpdateTestCase(FunctionTestCase):
    _function = validate_all_required_fields_included

    class DummySerializer(Serializer):
        age_not_required = IntegerField(required=False)
        name_required = CharField()

    def test(self):
        data = {}
        serializer = self.DummySerializer(data=data, partial=True)

        self.assertRaisesRegex(
            ValidationError,
            r'name_required field is required.',
            self._call_function,
            attrs=data, fields=serializer.fields
        )


class ValidateURLTestCase(APITestCase):
    def setUp(self):
        self.__temporary_image = TemporaryImageFactory()

    def test_raise_not_found(self):
        self.assertRaisesMessage(
            ValidationError,
            'Not found.',
            validate_image_url,
            image_url=BASE_IMAGE_URL
        )

    def test_validation_success(self):
        self.assertEqual(
            validate_image_url(self.__temporary_image.image_url),
            self.__temporary_image.image_url
        )
        self.assertTrue(not TemporaryImage.objects.filter(image_url=self.__temporary_image.image_url).exists())
