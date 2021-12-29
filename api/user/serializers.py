from random import randint
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from rest_framework.serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import datetime_from_epoch
from rest_framework.validators import UniqueValidator

from . import models, validators


class UserAccessTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        if hasattr(user, 'shopper'):
            token['user_type'] = 'shopper'
        elif hasattr(user, 'wholesaler'):
            token['user_type'] = 'wholesaler'

        models.OutstandingToken.objects.filter(jti=token['jti']).update(
            token = token,
        )
        
        return token


class UserRefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        token = super().validate(attrs)
        refresh = RefreshToken(token['refresh'])
    
        models.OutstandingToken.objects.create(
            user=models.User.objects.get(id=refresh['user_id']),
            jti=refresh['jti'],
            token=str(refresh),
            created_at=refresh.current_time,
            expires_at=datetime_from_epoch(refresh['exp']),
        )
        
        return token


class MembershipSerializer(ModelSerializer):
    class Meta:
        model = models.Membership
        fields = '__all__'


class UserSerializer(ModelSerializer):
    username = RegexField(r'^[a-zA-Z0-9]+$', min_length=4, max_length=20, validators=[UniqueValidator(queryset=models.User.objects.all())])
    password = RegexField(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[!-~]+$', max_length=128, min_length=10, write_only=True)

    class Meta:
        model = models.User
        fields = '__all__'

    def validate(self, attrs):
        if 'password' in attrs.keys():
            validators.PasswordSimilarityValidator().validate(attrs['password'], attrs['username'])

        return attrs

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = self._model.objects.create(**validated_data)

        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():            
            setattr(instance, key, value)
        
        instance.save()
        
        return instance


class ShopperSerializer(UserSerializer):
    phone = RegexField(r'^01[0|1|6|7|8|9][0-9]{7,8}$', validators=[UniqueValidator(queryset=models.Shopper.objects.all())])
    name = RegexField(r'^[가-힣]+$', max_length=20)
    nickname = RegexField(r'^[a-z0-9._]+$', min_length=4, max_length=20, required=False, validators=[UniqueValidator(queryset=models.Shopper.objects.all())])
    
    _model = models.Shopper
    class Meta:
        model = models.Shopper
        fields = '__all__'
        extra_kwargs = {            
            'height': {'min_value': 100, 'max_value': 250},
            'weight': {'min_value': 30, 'max_value': 200}
        }

    def __get_random_nickname(self):
        while True:
            nickname = 'dp_' + timezone.now().strftime('%m%d%H%M') + '_' + str(randint(1, 10**5))
            if not models.Shopper.objects.filter(nickname=nickname).exists():
                return nickname

    def create(self, validated_data):
        validated_data['nickname'] = self.__get_random_nickname()

        return super().create(validated_data)


class WholesalerSerializer(UserSerializer):
    phone = RegexField(r'^01[0|1|6|7|8|9][0-9]{7,8}$')
    company_registration_number = CharField(max_length=12, validators=[UniqueValidator(queryset=models.Wholesaler.objects.all())])

    _model = models.Wholesaler
    class Meta:
        model = models.Wholesaler
        fields = '__all__'


class UserPasswordSerializer(Serializer):
    current_password = CharField(min_length=10, max_length=128)
    new_password = RegexField(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[!-~]+$', max_length=128, min_length=10)

    def __init__(self, data, user):
        super().__init__(data=data)
        self.user = user

    def validate(self, attrs):
        if not self.user.check_password(attrs['current_password']):
            raise ValidationError('current password does not correct.')
        elif attrs['current_password'] == attrs['new_password']:
            raise ValidationError('new password is same as the current password.')
    
        validators.PasswordSimilarityValidator().validate(attrs['new_password'], self.user.username)

        return attrs
