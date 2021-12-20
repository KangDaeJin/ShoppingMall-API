from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from . import models, serializers, permissions

from django.forms.models import model_to_dict

def get_result_message(status=200, message='success', id=0):
    result = {
        'code': status,
        'message': message, 
    }

    if id:
        result['id'] = id

    return result

class UserAccessTokenView(TokenObtainPairView):
    serializer_class = serializers.UserAccessTokenSerializer


class UserRefreshTokenView(TokenRefreshView):
    serializer_class = serializers.UserRefreshTokenSerializer


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedExceptCreate]    

    def __pop_user(self, data):
        if 'user' not in data.keys():
            return data

        user_data = data.pop('user')
        for key, value in user_data.items():
            data[key] = value

        return data

    def __push_user(self, data):
        user_keys = [field.name for field in models.User._meta.get_fields()]
        user_data = {}
        for key in user_keys:
            if key in data.keys():
                user_data[key] = data.pop(key)
        data['user'] = user_data

        return data

    def _get_model_instance(self, user):
        return user

    def get(self, request):
        serializer = self._serializer_class(instance=self._get_model_instance(request.user))

        data = self.__pop_user(serializer.data)
        data.pop('password')

        return Response(data)

    def post(self, request):
        data = self.__push_user(request.data)
        serializer = self._serializer_class(data=data)

        if not serializer.is_valid():
            return Response(get_result_message(400, self.__pop_user(serializer.errors)), status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        
        return Response(get_result_message(id=user.user_id))

    def patch(self, request):
        if 'password' in request.data:
            return Response(get_result_message(400, 'password modification is not allowed in PATCH method'), status=status.HTTP_400_BAD_REQUEST)
        
        data = self.__push_user(request.data)
        serializer = self._serializer_class(instance=self._get_model_instance(request.user), data=data, partial=True)

        if not serializer.is_valid():
            return Response(get_result_message(400, self.__pop_user(serializer.errors)), status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        return Response(get_result_message(id=user.user_id))

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()

        return Response(get_result_message(id=user.id), status=status.HTTP_200_OK)


class ShopperDetailView(UserDetailView):
    _serializer_class = serializers.ShopperSerializer

    def _get_model_instance(self, user):
        return user.shopper


class WholesalerDetailView(UserDetailView):
    _serializer_class = serializers.WholesalerSerializer

    def _get_model_instance(self, user):
        return user.wholesaler


class UserPasswordView(APIView):
    def __discard_refresh_token_by_user_id(self, user_id):
        all_tokens = models.OutstandingToken.objects.filter(user_id=user_id, expires_at__gt=timezone.now()).all()

        discarding_tokens = []
        for token in all_tokens:
            if not hasattr(token, 'blacklistedtoken'):
                discarding_tokens.append(models.BlacklistedToken(token=token))
    
        models.BlacklistedToken.objects.bulk_create(discarding_tokens)

    def patch(self, request):
        user = request.user
        data = request.data
        data['id'] = user.id
        serializer = serializers.UserPasswordSerializer(data=data)

        if not serializer.is_valid():
            return Response(get_result_message(400, serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.last_update_password = timezone.now()
        user.save()
        self.__discard_refresh_token_by_user_id(user.id)

        return Response(get_result_message(id=user.id), status=status.HTTP_200_OK)
