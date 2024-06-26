from datetime import date

from django.db.models.query import Prefetch
from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.db.models import Sum, F, Case, When

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.exceptions import PermissionDenied
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase

from common.utils import get_response, get_response_body
from common.views import upload_image_view
from common.permissions import IsAuthenticatedShopper, IsAuthenticatedWholesaler
from product.models import Product
from coupon.serializers import CouponSerializer
from coupon.models import Coupon
from .models import (
    ShopperShippingAddress, User, Shopper, Wholesaler, Building, ProductLike, PointHistory, Cart,
    ShopperCoupon,
)
from .serializers import (
    IssuingTokenSerializer, RefreshingTokenSerializer, TokenBlacklistSerializer,
    UserPasswordSerializer, ShopperSerializer, WholesalerSerializer, BuildingSerializer,
    ShopperShippingAddressSerializer, PointHistorySerializer, CartSerializer, ShopperCouponSerializer,
)
from .paginations import PointHistoryPagination
from .permissions import AllowAny, IsAuthenticated, IsAuthenticatedExceptCreate


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_business_registration_image(request):
    return upload_image_view(request, 'business_registration')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_buildings(request):
    serializer = BuildingSerializer(instance=Building.objects.all().prefetch_related(Prefetch('floors')), many=True)

    return get_response(data=serializer.data)


@api_view(['PATCH'])
def change_password(request):    
    serializer = UserPasswordSerializer(instance=request.user, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return get_response(data={'id': request.user.id})


@api_view(['GET'])
@permission_classes([AllowAny])
def is_unique(request):
    mapping = {
        'username': {'model': User, 'column': 'username'},
        'shopper_nickname': {'model': Shopper, 'column': 'nickname'},
        'wholesaler_name': {'model': Wholesaler, 'column': 'name'},
        'wholesaler_company_registration_number': {'model': Wholesaler, 'column': 'company_registration_number'},
    }

    request_data = list(request.query_params.items())
    if len(request.query_params) != 1:
        return get_response(status=HTTP_400_BAD_REQUEST, message='Only one parameter is allowed.')
    elif request_data[0][0] not in mapping.keys():
        return get_response(status=HTTP_400_BAD_REQUEST, message='Invalid parameter name.')

    mapping_data = mapping[request_data[0][0]]
    if mapping_data['model'].objects.filter(**{mapping_data['column']: request_data[0][1]}).exists():
        return get_response(data={'is_unique': False})

    return get_response(data={'is_unique': True})


class TokenView(TokenViewBase):
    def post(self, request, *args, **kwargs):
        return get_response(status=HTTP_201_CREATED, data=super().post(request, *args, **kwargs).data)


class IssuingTokenView(TokenView):
    serializer_class = IssuingTokenSerializer


class RefreshingTokenView(TokenView):
    serializer_class = RefreshingTokenSerializer


class BlacklistingTokenView(TokenView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data = get_response_body(response.status_code, data={'id': request.user.id})
        return response


class UserView(GenericAPIView):
    permission_classes = [IsAuthenticatedExceptCreate]

    def get(self, request):
        serializer = self.get_serializer(self._get_user())

        return get_response(data=serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return get_response(status=HTTP_201_CREATED, data={'id': user.user_id})

    def patch(self, request):
        if set(request.data).difference(self._patchable_fields):
            return get_response(status=HTTP_400_BAD_REQUEST, message='It contains requests for fields that do not exist or cannot be modified.')

        serializer = self.get_serializer(self._get_user(), request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return get_response(data={'id': user.id})

    def delete(self, request):
        user = self._get_user()
        user.delete()

        return get_response(data={'id': user.id})


class ShopperView(UserView):
    serializer_class = ShopperSerializer
    _patchable_fields = set(['email', 'nickname', 'height', 'weight'])

    def _get_user(self):
        return self.request.user.shopper

    def get_queryset(self):
        return Shopper.objects.filter(is_active=True)


class WholesalerView(UserView):
    serializer_class = WholesalerSerializer
    _patchable_fields = ['mobile_number', 'email']

    def _get_user(self):
        return self.request.user.wholesaler

    def get_queryset(self):
        return Wholesaler.objects.filter(is_active=True)


class PointHistoryView(GenericAPIView):
    permission_classes = [IsAuthenticatedShopper]
    pagination_class = PointHistoryPagination
    serializer_class = PointHistorySerializer

    def filter_queryset(self, queryset):
        if 'type' in self.request.query_params:
            if self.request.query_params['type'] == 'USE':
                queryset = queryset.filter(point__lt=0)
            elif self.request.query_params['type'] == 'SAVE':
                queryset = queryset.filter(point__gt=0)
    
        return queryset

    def get_queryset(self):
        queryset = PointHistory.objects.select_related('order').filter(shopper=self.request.user.shopper)

        return self.filter_queryset(queryset)

    def get(self, request):
        serializer = self.get_serializer(self.paginate_queryset(self.get_queryset()), many=True)

        return get_response(data=self.get_paginated_response(serializer.data).data)


class ProductLikeView(APIView):
    permission_classes = [IsAuthenticatedShopper]

    def get_queryset(self):
        return ProductLike.objects.all()

    @transaction.atomic
    def post(self, request, product_id):
        shopper = request.user.shopper
        product = get_object_or_404(Product, id=product_id)

        if self.get_queryset().filter(shopper=shopper, product=product).exists():
            return get_response(status=HTTP_400_BAD_REQUEST, message='Duplicated user and product')

        ProductLike.objects.create(shopper=shopper, product=product)
        return get_response(status=HTTP_201_CREATED, data={'shopper_id': shopper.user_id, 'product_id': product.id})

    @transaction.atomic
    def delete(self, request, product_id):
        shopper = request.user.shopper
        product = get_object_or_404(Product, id=product_id)

        if not self.get_queryset().filter(shopper=shopper, product=product).exists():
            return get_response(status=HTTP_400_BAD_REQUEST, message='You are deleting non exist likes')

        product_like = ProductLike.objects.get(shopper=shopper, product=product)
        product_like.delete()

        return get_response(data={'shopper_id': shopper.user_id, 'product_id': product_id})


class CartViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedShopper]
    serializer_class = CartSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'cart_id'
    lookup_value_regex = r'[0-9]+'
    __patchable_fields = set(['count'])
    pagination_class = None

    def get_queryset(self):
        queryset = self.request.user.shopper.carts.all()
        if self.action == 'list':
            queryset = queryset.select_related(
                'option__product_color__product'
            ).prefetch_related('option__product_color__product__images')

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        aggregate_data = queryset.aggregate(
            total_sale_price=Sum(F('option__product_color__product__sale_price') * F('count')),
            total_base_discounted_price=Sum(F('option__product_color__product__base_discounted_price') * F('count'))
        )

        response_data = {'results': serializer.data}
        response_data.update(aggregate_data)

        return get_response(data=response_data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'shopper': request.user.shopper}, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return get_response(status=HTTP_201_CREATED, data={'option_id': [data['option'] for data in request.data]})

    def partial_update(self, request, cart_id):
        if set(request.data).difference(self.__patchable_fields):
            return get_response(status=HTTP_400_BAD_REQUEST, message='It contains requests for fields that do not exist or cannot be modified.')

        cart = self.get_object()
        serializer = self.get_serializer(cart, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()

        return get_response(data={'id': cart.id})

    def remove(self, request):
        delete_id_list = request.data.get('id', None)
        if delete_id_list is None:
            return get_response(status=HTTP_400_BAD_REQUEST, message='list of id is required.')
        elif not isinstance(delete_id_list, list) or not all(isinstance(id, int) for id in delete_id_list):
            return get_response(status=HTTP_400_BAD_REQUEST, message='values in the list must be integers.')

        queryset = self.get_queryset()
        if queryset.filter(id__in=delete_id_list).count() != len(delete_id_list):
            raise PermissionDenied()

        self.get_queryset().filter(id__in=delete_id_list).delete()

        return get_response(data={'id': delete_id_list})


class ShopperShippingAddressViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedShopper]
    serializer_class = ShopperShippingAddressSerializer
    lookup_url_kwarg = 'shipping_address_id'
    lookup_value_regex = r'[0-9]+'

    def get_queryset(self):
        order_condition = [Case(When(is_default=True, then=1), default=2), '-id']
        return self.request.user.shopper.addresses.all().order_by(*order_condition)

    def list(self, request):
        serializer = self.get_serializer(instance=self.get_queryset(), many=True)

        return get_response(data=serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipping_address = serializer.save(shopper=request.user.shopper)

        return get_response(status=HTTP_201_CREATED, data={'id': shipping_address.id})

    def partial_update(self, request, shipping_address_id):
        shipping_address = self.get_object()
        serializer = self.get_serializer(
            shipping_address, request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        shipping_address = serializer.save(shopper=request.user.shopper)

        return get_response(data={'id': shipping_address.id})

    def destroy(self, request, shipping_address_id):
        shipping_address = self.get_object()
        shipping_address.delete()

        return get_response(data={'id': int(shipping_address_id)})

    def get_default_address(self, request):
        queryset = self.get_queryset()

        if not queryset.exists():
            return get_response(data={})
        elif queryset.filter(is_default=True).exists():
            try:
                shipping_address = queryset.get(is_default=True)
            except ShopperShippingAddress.MultipleObjectsReturned:
                shipping_address = queryset.filter(is_default=True).first()
        else:
            shipping_address = queryset.first()

        serializer = self.get_serializer(shipping_address)

        return get_response(data=serializer.data)


class ShopperCouponViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedShopper]
    lookup_field = 'id'
    lookup_url_kwarg = 'cart_id'
    lookup_value_regex = r'[0-9]+'

    def get_serializer_class(self):
        if self.action == 'list': 
            return CouponSerializer
        elif self.action == 'create': 
            return ShopperCouponSerializer

    def get_queryset(self):
        return self.request.user.shopper.coupons.filter(
            shoppercoupon__is_used=False, shoppercoupon__end_date__gte=date.today()
        ).order_by('-shoppercoupon__coupon')

    def list(self, request):
        response = super().list(request)
        return get_response(data=response.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(shopper=request.user.shopper)

        return get_response(status=HTTP_201_CREATED, data={'coupon_id': request.data['coupon']})

# 복붙..