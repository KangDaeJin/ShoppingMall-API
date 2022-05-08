from factory import Sequence, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from factory.faker import Faker
from factory.fuzzy import FuzzyText, FuzzyInteger

from product.test.factory import create_options


def create_order_with_items(size=3):
    order = OrderFactory()
    for option in create_options(size):
        OrderItemFactory(order=order, option=option)
    
    return order


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = 'order.Order'

    shopper = SubFactory('user.test.factory.ShopperFactory')
    shipping_address = SubFactory('order.test.factories.ShippingAddressFactory')


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = 'order.OrderItem'

    order = SubFactory(OrderFactory)
    option = SubFactory('product.test.factory.OptionFactory')
    status = SubFactory('order.test.factories.StatusFactory')
    sale_price = LazyAttribute(lambda obj: obj.option.product_color.product.sale_price)
    base_discount_price = LazyAttribute(lambda obj: obj.sale_price - obj.option.product_color.product.base_discounted_price)
    membership_discount_price = LazyAttribute(lambda obj: int((obj.sale_price - obj.base_discount_price) * float(obj.order.shopper.membership.discount_rate) // 100))
    payment_price = LazyAttribute(lambda obj: obj.sale_price - obj.base_discount_price - obj.membership_discount_price)
    earned_point = LazyAttribute(lambda obj: obj.payment_price // 100)


class StatusFactory(DjangoModelFactory):
    class Meta:
        model = 'order.Status'

    id = Sequence(lambda num: num)
    name = FuzzyText()


class ShippingAddressFactory(DjangoModelFactory):
    class Meta:
        model = 'order.ShippingAddress'

    receiver_name = Faker('name', locale='ko-KR')
    mobile_number = Sequence(lambda num: '010%08d' % num)
    phone_number = Sequence(lambda num: '02%08d' % num)
    zip_code = Faker('postcode', locale='ko-KR')
    base_address = Faker('address', locale='ko-KR')
    detail_address = Faker('address_detail', locale='ko-KR')
    shipping_message = '부재 시 집 앞에 놔주세요.'


class RefundFacotry(DjangoModelFactory):
    class Meta:
        model = 'order.Refund'
    
    price = FuzzyInteger(1000, 5000000)