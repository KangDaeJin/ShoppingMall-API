from django.db.models import Q
from django.db.models.query import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import APIException, NotFound

from common.utils import get_response
from common.exceptions import BadRequestError
from product.models import Product, ProductImage, Option
from .models import (
    Order, OrderItem, ShippingAddress, Status,
)
from .serializers import (
    OrderItemSerializer, OrderSerializer, OrderWriteSerializer, OrderItemWriteSerializer, ShippingAddressSerializer
)
from .permissions import OrderPermission, OrderItemPermission

from rest_framework.permissions import AllowAny
from django.db import connection
from django.forms import model_to_dict

class OrderViewSet(GenericViewSet):
    permission_classes = [OrderPermission]
    lookup_field = 'id'
    lookup_url_kwarg = 'order_id'
    __actions_requiring_write_serilaizer = ['create', 'partial_update']
    __patchable_fields = ['shipping_address']

    def get_serializer_class(self):
        # if self.action in self.__actions_requiring_write_serilaizer:
        #     return OrderWriteSerializer

        if self.action in ['create']:
            return OrderWriteSerializer
        elif self.action == 'update_shipping_address':
            return ShippingAddressSerializer
        
        return OrderSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'wholesaler'):
            pass
        elif hasattr(self.request.user, 'shopper'):
            condition = Q(shopper=self.request.user.shopper)
        else:
            raise APIException('Unrecognized user.')

        image = ProductImage.objects.filter(sequence=1)
        items = OrderItem.objects.select_related('option__product_color__product', 'status').prefetch_related(Prefetch('option__product_color__product__images', queryset=image))
        
        return Order.objects.select_related('shipping_address').prefetch_related(Prefetch('items', queryset=items)).filter(condition)

    def list(self, request):
        return get_response(data=self.get_serializer(self.get_queryset(), many=True).data)        

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'shopper': request.user.shopper})

        if not serializer.is_valid():
            return get_response(status=HTTP_400_BAD_REQUEST, message=serializer.errors)

        # todo
        # 결제 로직 + 결제 관련 상태 (입금 대기 or 결제 완료 or 결제 오류)

        order = serializer.save(status_id=101)

        return get_response(data={'id': order.id})
        # return get_response(data=connection.queries)
    
    def retrieve(self, request, id):
        return get_response(data=self.get_serializer(self.get_object()).data)

    @action(['put'], True, 'shipping-address')
    def update_shipping_address(self, request, order_id):
        serializer = self.get_serializer(data=request.data, context={'order': self.get_object()})
        if not serializer.is_valid():
            return get_response(status=HTTP_400_BAD_REQUEST, message=serializer.errors)

        serializer.save()

        return get_response(data={'id': order_id})

    # @action(['post'], False)
    # def cancel(self, reqeust):
    #     pass



class OrderItemViewSet(GenericViewSet):
    permission_classes = [OrderItemPermission]
    serializer_class = OrderItemWriteSerializer
    # queryset = OrderItem
    lookup_field = 'id'
    lookup_url_kwarg = 'item_id'
    __patchable_fields = set(['option'])
 
    def get_queryset(self):
        if hasattr(self.request.user, 'shopper'):
            condition = Q(order__shopper=self.request.user.shopper)
        else:
            raise APIException('Unrecognized user.')

        if 'order' in self.request.data:
            condition &= Q(order_id=self.request.data['order'])
        if 'items' in self.request.data:
            condition &= Q(id__in=self.request.data['items'])

        return OrderItem.objects.select_related('order', 'option__product_color').filter(condition)

    def partial_update(self, request, item_id):
        if set(request.data).difference(self.__patchable_fields):
            return get_response(status=HTTP_400_BAD_REQUEST, message='It contains requests for fields that do not exist or cannot be modified.')

        serializer = self.get_serializer(self.get_object(), request.data, partial=True)
        if not serializer.is_valid():
            return get_response(status=HTTP_400_BAD_REQUEST, message=serializer.errors)

        serializer.save()

        return get_response(data={'id': item_id})

    # @action(['post'], False)
    # def cancel(self, request):
    #     if 'items' not in request.data:
    #         return get_response(status=HTTP_400_BAD_REQUEST, message='Requests must include items field.')
        
    #     if hasattr(self.request.user, 'shopper') and 'order' not in request.data:
    #         return get_response(status=HTTP_400_BAD_REQUEST, message='Requests must include order field.')

    #     queryset = self.get_queryset()
    #     if len(request.data['items']) != len(queryset):
    #         return get_response(status=HTTP_400_BAD_REQUEST, message='Invalid item requested.')

    #     serializer = self.get_serializer(self.get_queryset(), many=True)
    #     serializer.update(serializer.instance, 'cancellation_information')        

    #     return get_response(data=serializer.data)

    # todo 발주확인 관련


class ClaimViewSet(GenericViewSet):
    permission_classes = [OrderPermission]
    serializer_class = OrderItemWriteSerializer
    # lookup_field = 'id'
    # lookup_url_kwarg = 'order_id'

    def get_queryset(self):
        condition = Q(order__shopper=self.request.user.shopper) & Q(order_id=self.kwargs['order_id'])
        if 'items' in self.request.data:
            condition &= Q(id__in=self.request.data['items'])

        queryset = OrderItem.objects.filter(condition)

        self.__check_queryset(queryset)

        return queryset

    def __check_queryset(self, queryset):
        if 'items' in self.request.data and len(queryset) != len(self.request.data['items']):
            raise BadRequestError('It contains invalid items.')
        
        if len(queryset) == 0:
            raise NotFound('The order does not exist.')

        status_set = list(set([instance.status_id for instance in queryset]))

        if len(status_set) != 1:
            raise BadRequestError('It cannot request multiple status items at once.')

        if self.action == 'cancel' and status_set[0] not in [100, 101]:
            raise BadRequestError('The items cannot be canceled.')

    @action(['post'], False)
    def cancel(self, request, order_id):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        serializer.update(queryset, 'cancellation_information')
        #todo 환불

        return get_response(data={'id': [item.id for item in queryset]})
