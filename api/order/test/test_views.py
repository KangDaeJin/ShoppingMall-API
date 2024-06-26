from dateutil.relativedelta import relativedelta

from django.db.models import Count
from django.utils import timezone

from common.test.test_cases import ViewTestCase
from common.utils import REQUEST_DATE_FORMAT
from user.test.factories import UserFactory, ShopperCouponFactory
from product.models import Option
from product.test.factories import OptionFactory
from coupon.models import ALL_PRODUCT_COUPON_CLASSIFICATIONS
from coupon.test.factories import CouponClassificationFactory
from .factories import StatusHistoryFactory, create_orders_with_items, OrderItemFactory, ShippingAddressFactory, StatusFactory
from .test_serializers import (
    get_order_item_queryset, get_order_queryset, get_shipping_address_test_data, get_order_test_data, 
    get_order_confirm_result, get_delivery_test_data, get_delivery_result,
)
from ..paginations import OrderPagination
from ..models import (
    PAYMENT_COMPLETION_STATUS, DELIVERY_PREPARING_STATUS, DELIVERY_PROGRESSING_STATUS, NORMAL_STATUS, 
    Order, OrderItem, Status,
)
from ..serializers import (
    ShippingAddressSerializer, OrderItemWriteSerializer, OrderSerializer, OrderWriteSerializer, OrderItemStatisticsSerializer,
    StatusHistorySerializer, OrderConfirmSerializer, DeliverySerializer,
)
from ..views import OrderViewSet


class OrderViewSetTestCase(ViewTestCase):
    _url = '/orders'
    _view_class = OrderViewSet

    @classmethod
    def setUpTestData(cls):
        cls.__easyadmin_user = UserFactory(username='easyadmin', is_admin=True)
        cls._set_shopper()
        cls.__shipping_address = ShippingAddressFactory()
        cls.__payment_completion_status = StatusFactory(id=PAYMENT_COMPLETION_STATUS)
        cls.__all_product_coupon_classification = CouponClassificationFactory(id=ALL_PRODUCT_COUPON_CLASSIFICATIONS[0])
        cls.__orders = create_orders_with_items(2, 3, False,
            {'shopper': cls._user, 'shipping_address': cls.__shipping_address}, 
            {'status': cls.__payment_completion_status, 'shopper_coupon__coupon__classification': cls.__all_product_coupon_classification},
        )
        StatusFactory(id=DELIVERY_PREPARING_STATUS)
        StatusFactory(id=DELIVERY_PROGRESSING_STATUS)

    def setUp(self):
        self._set_authentication()

    def __easyadmin_set_up(self):
        self._user = self.__easyadmin_user
        self._set_authentication()

    def __get_queryset(self, **filters):
        queryset = Order.objects
        item_queryset = get_order_item_queryset()
        if 'status' in filters:
            status = Status.objects.get(name=filters['status'])
            item_queryset = item_queryset.filter(status=status)
            queryset = queryset.filter(items__status=status).annotate(count=Count('id')).order_by('-id')
        if 'start_date' in filters and 'end_date' in filters:
            queryset = queryset.filter(created_at__range=[
                filters['start_date'], 
                filters['end_date'] + ' 23:59:59',
            ])
            
        return get_order_queryset(queryset, item_queryset).filter(shopper_id=self._user.id)

    def __set_detail_url(self):
        self.__order = self.__orders[0]
        self._url += f'/{self.__order.id}'

    def __test_pagination_list(self, **query_params):
        self._get(query_params)

        self._assert_pagination_success(OrderSerializer(self.__get_queryset(**query_params), many=True).data)

    def test_pagination_class(self):
        self._test_pagination_class(OrderPagination, 10)

    def test_list(self):
        self.__test_pagination_list()

    def test_status_filter_list(self):
        order_item = OrderItem.objects.filter(order__shopper_id=self._user.id).only('status').first()
        order_item.status_id = DELIVERY_PREPARING_STATUS
        order_item.save()

        self.__test_pagination_list(status=self.__payment_completion_status.name)

    def test_date_filter_list(self):
        order = Order.objects.filter(shopper_id=self._user.id).only('created_at').first()
        order.created_at = timezone.now() - relativedelta(months=1)
        order.save()
        start_date = (order.created_at + relativedelta(days=1)).strftime(REQUEST_DATE_FORMAT)
        end_date = timezone.now().strftime(REQUEST_DATE_FORMAT)

        self.__test_pagination_list(start_date=start_date, end_date=end_date)

    def test_create(self):
        options = Option.objects.select_related('product_color__product').all()
        shopper_coupons = [ShopperCouponFactory(
            shopper = self._user,
            is_used = False,
            coupon__classification = self.__all_product_coupon_classification,
            coupon__discount_price = discount_price,
        ) for discount_price in [None, True]] + [None] * (len(options) - 2)
        self._test_data = get_order_test_data(self.__shipping_address, options, self._user, shopper_coupons)
        self._post(format='json')

        self._assert_success_and_serializer_class(OrderWriteSerializer)

    def test_retreive(self):
        self.__set_detail_url()
        order = self.__get_queryset().get(id=self.__order.id)
        self._get()
        
        self._assert_success()
        self.assertDictEqual(self._response_data, OrderSerializer(order).data)

    def test_update_shipping_address(self):
        self.__set_detail_url()
        self._url += '/shipping-address'
        self._test_data = get_shipping_address_test_data(ShippingAddressFactory.build())
        self._put()

        self._assert_success_and_serializer_class(ShippingAddressSerializer)
        self.assertEqual(self._response_data['id'], self.__order.id)

    def test_confirm(self):
        self.__easyadmin_set_up()
        self._url += '/confirm'
        expected_result = get_order_confirm_result(OrderItem.objects.all(), 200)
        self._test_data = {'order_items': sum([data for data in list(expected_result.values())], [])}
        self._post()

        self._assert_success_and_serializer_class(OrderConfirmSerializer, False)
        self.assertDictEqual(self._response_data, expected_result)

    def test_delivery_request_data_size_validation(self):
        self.__easyadmin_set_up()
        self._url += '/delivery'
        self._test_data = [''] * 51
        self._post(format='json')

        self._assert_failure(400, 'You can only request up to 50 at a time.')

    def test_delivery(self):
        self.__easyadmin_set_up()
        self._url += '/delivery'
        order_items = OrderItem.objects.all()
        for order_item in order_items:
            order_item.status_id = DELIVERY_PREPARING_STATUS
        OrderItem.objects.bulk_update(order_items, ['status_id'])
        self._test_data = [get_delivery_test_data(order) for order in self.__orders]
        expected_result = get_delivery_result(self._test_data)
        self._post(format='json')

        self._assert_success_and_serializer_class(DeliverySerializer, False)
        self.assertDictEqual(self._response_data, expected_result)
        

class OrderItemViewSetTestCase(ViewTestCase):
    _url = '/orders/items'

    @classmethod
    def setUpTestData(cls):
        cls._set_shopper()

        for status_id in NORMAL_STATUS:
            status = StatusFactory(id=status_id)
            if status_id == PAYMENT_COMPLETION_STATUS:
                payment_completion_status_instance = status

        cls.__order_item = OrderItem.objects.select_related('status', 'option__product_color').get(
            id=OrderItemFactory(order__shopper=cls._user, status=payment_completion_status_instance).id)

    def setUp(self):
        self._set_authentication()

    def test_partial_update_with_non_patchable_field(self):
        self._url += f'/{self.__order_item.id}'
        self._patch({'sale_price': 1000})

        self._assert_failure_for_non_patchable_field()

    def test_partial_update(self):
        self._url += f'/{self.__order_item.id}'
        self._patch({'option': OptionFactory(product_color=self.__order_item.option.product_color).id})

        self._assert_success_and_serializer_class(OrderItemWriteSerializer)

    def test_get_statistics(self):
        self._url += '/statistics'
        self._get()

        self._assert_success()
        self.assertListEqual(self._response_data, OrderItemStatisticsSerializer([{
            'status__name': self.__order_item.status.name,
            'count': 1,
        }], many=True).data)


class ClaimViewSetTestCase(ViewTestCase):
    pass


class StatusHistoryTestCase(ViewTestCase):
    _url = '/orders/items'

    @classmethod
    def setUpTestData(cls):
        cls._set_shopper()
        cls.__order_item = OrderItemFactory(order__shopper=cls._user)
        cls._url += f'/{cls.__order_item.id}/status-histories'

    def setUp(self):
        self._set_authentication()

    def test_get(self):
        status_histories = StatusHistoryFactory.create_batch(3, order_item=self.__order_item)
        self._get()

        self._assert_success()
        self.assertListEqual(self._response_data, StatusHistorySerializer(status_histories, many=True).data)