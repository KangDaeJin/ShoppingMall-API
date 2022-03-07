from freezegun import freeze_time

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from common.test.test_cases import ViewTestCase, FREEZE_TIME, FREEZE_TIME_AUTO_TICK_SECONDS
from common.utils import datetime_to_iso
from .factory import get_factory_password, get_factory_authentication_data
from ..models import BlacklistedToken, User, Shopper, Wholesaler
from ..serializers import IssuingTokenSerializer, RefreshingTokenSerializer, ShopperSerializer, WholesalerSerializer


class TokenViewTestCase(ViewTestCase):
    @classmethod
    def _issue_token(cls):
        cls._set_user()
        token_serializer = IssuingTokenSerializer(data=get_factory_authentication_data(cls._user))
        token_serializer.is_valid()
        cls._test_data = token_serializer.validated_data

    def _refresh_token(self):
        token_serializer = RefreshingTokenSerializer(data=self._test_data)
        token_serializer.is_valid()

    def _assert_token(self):
        self.assertTrue(AccessToken(self._response_data['access']))
        self.assertTrue(RefreshToken(self._response_data['refresh']))
    
    def _assert_failure(self, expected_message):
        super()._assert_failure(401, expected_message)


class IssuingTokenViewTestCase(TokenViewTestCase):
    _url = '/token/'

    @classmethod
    def setUpTestData(cls):
        cls._set_user()

    def setUp(self):
        self._test_data = get_factory_authentication_data(self._user)

    def test_success(self):
        self._post()
    
        self._assert_success()
        self._assert_token()
        
    def test_wrong_password(self):
        self._test_data['password'] = 'wrong_password'
        self._post()

        self._assert_failure('No active account found with the given credentials')

    def test_non_existent_user(self):
        self._test_data['username'] = 'non_existent_user'
        self._post()

        self._assert_failure('No active account found with the given credentials')
        

class RefreshingTokenViewTestCase(TokenViewTestCase):
    _url = '/token/refresh/'

    @classmethod
    def setUpTestData(cls):
        cls._issue_token()

    def test_success(self):
        self._post()

        self._assert_success()
        self._assert_token()

    def test_failure_using_blacklisted_token(self):
        self._refresh_token()
        self._post()

        self._assert_failure('Token is blacklisted')

    def test_failure_using_abnormal_token(self):
        self._test_data = {'refresh': 'abnormal_token'}
        self._post()

        self._assert_failure('Token is invalid or expired')


class BlacklistingTokenViewTestCase(TokenViewTestCase):
    _url = '/token/blacklist/'        

    @classmethod
    def setUpTestData(cls):
        cls._issue_token()

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self._test_data['access'])

    def test_success(self):
        self._post()

        self._assert_success_with_id_response()
        self.assertEqual(self._response_data['id'], self._user.id)
        self.assertEqual(BlacklistedToken.objects.get(token__token=self._test_data['refresh']).token.user_id, self._user.id)


class ShopperViewTestCase(ViewTestCase):
    fixtures = ['membership']
    _url = '/user/shopper/'

    @classmethod
    def setUpTestData(cls):
        cls._set_shopper()

    def setUp(self):
        self._set_authentication()

    def test_get(self):
        self._get()

        self._assert_success()
        self.assertDictEqual(self._response_data, ShopperSerializer(instance=self._user).data)

    def test_post(self):
        self._unset_authentication()
        self._test_data = {
            "name": "테스트",
            "birthday": "2021-11-20",
            "gender": 1,
            "email": "test@naver.com",
            "mobile_number": "01011111111",
            "username": "xptmxm",
            "password": "Testtest00"
        }
        self._post()
        self._user = Shopper.objects.get(username=self._test_data['username'])

        self._assert_success_with_id_response()
        self.assertEqual(self._response_data['id'], self._user.id)
        self.assertTrue(self._user.check_password(self._test_data['password']))

    def test_patch(self):
        self._test_data = {
            'email': 'user@omios.com',
            'nickname': 'patch_test',
            'height': '180',
            'weight': 70
        }
        self._patch()
        self._user = Shopper.objects.get(id=self._user.id)

        self._assert_success_with_id_response()
        self.assertEqual(self._response_data['id'], self._user.id)
        self.assertEqual(self._user.email, self._test_data['email'])
        self.assertEqual(self._user.nickname, self._test_data['nickname'])
        self.assertEqual(self._user.height, int(self._test_data['height']))
        self.assertEqual(self._user.weight, self._test_data['weight'])

    def test_patch_with_non_existent_field(self):
        self._test_data = {
            'email': 'user@omios.com',
            'non_existent_field': 'test',
        }
        self._patch()

        self._assert_failure(400, 'It contains requests for fields that do not exist or cannot be modified.')

    def test_patch_with_non_modifiable_field(self):
        self._test_data = {
            'nickname': 'patch_error_test',
            'password': 'test',
        }
        self._patch()

        self._assert_failure(400, 'It contains requests for fields that do not exist or cannot be modified.')

    @freeze_time(FREEZE_TIME)
    def test_delete(self):
        self._delete()
        self._user = Shopper.objects.get(id=self._user.id)

        self._assert_success_with_id_response()
        self.assertEqual(self._response_data['id'], self._user.id)
        self.assertTrue(not self._user.is_active)
        self.assertEqual(datetime_to_iso(self._user.deleted_at), FREEZE_TIME)


class WholesalerViewTestCase(ViewTestCase):
    pass


class ChangePasswordTestCase(ViewTestCase):
    _url = '/user/password/'

    @classmethod
    def setUpTestData(cls):
        cls._set_user()

    @freeze_time(FREEZE_TIME)
    def test_success(self):
        self._set_authentication()
        self._test_data = {
            'current_password': get_factory_password(self._user),
            'new_password': 'New_password00'
        }
        self._patch()
        self._user = User.objects.get(id=self._user.id)

        self._assert_success_with_id_response()
        self.assertEqual(self._response_data['id'], self._user.id)
        self.assertTrue(self._user.check_password(self._test_data['new_password']))
        self.assertEqual(datetime_to_iso(self._user.last_update_password), FREEZE_TIME)


class IsUniqueTestCase(ViewTestCase):
    fixtures = ['membership']
    _url = '/user/unique/'

    @classmethod
    def setUpTestData(cls):
        cls.__shopper = cls._create_shopper()[0]
        # cls.__wholesaler = cls._create_wholesaler()

    def test_is_unique_username(self):
        self._get({'username': 'unique_username'})

        self._assert_success_with_is_unique_response(True)

    def test_is_not_unique_username(self):
        self._get({'username': self.__shopper.username})

        self._assert_success_with_is_unique_response(False)

    def test_is_unique_shopper_nickname(self):
        self._get({'shopper_nickname': 'unique_nickname'})

        self._assert_success_with_is_unique_response(True)

    def test_is_not_unique_shopper_nickname(self):
        self._get({'shopper_nickname': self.__shopper.nickname})

        self._assert_success_with_is_unique_response(False)

    def test_is_unique_wholesaler_name(self):
        pass

    def test_is_not_unique_wholesaler_name(self):
        pass

    def test_is_unique_wholesaler_company_registration_number(self):
        pass

    def test_is_not_unique_wholesaler_company_registration_number(self):
        pass

    def test_no_parameter_validation(self):
        self._get()

        self._assert_failure(400, 'Only one parameter is allowed.')

    def test_many_paramter_validation(self):
        self._get({'parameter1': 'parameter1', 'parameter2': 'parameter2'})

        self._assert_failure(400, 'Only one parameter is allowed.')

    def test_invalid_parameter_validation(self):
        self._get({'invalid_parameter': 'test'})

        self._assert_failure(400, 'Invalid parameter name.')