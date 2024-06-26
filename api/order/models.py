import random
import string

from django.db.models import (
    Model, BigAutoField, AutoField, ForeignKey, OneToOneField,
    IntegerField, BigIntegerField, CharField, BooleanField, DateTimeField,
    DO_NOTHING
)
from django.utils import timezone

from common.utils import DEFAULT_DATETIME_FORMAT


DEPOSIT_WAITING_STATUS = 100
PAYMENT_COMPLETION_STATUS = 101
DELIVERY_PREPARING_STATUS = 200
DELIVERY_PROGRESSING_STATUS = 201
DELIVERY_COMPLETION_STATUS = 202
PURCHASE_CONFIRMATION_STATUS = 203
BEFORE_DELIVERY_STATUS = [DEPOSIT_WAITING_STATUS, PAYMENT_COMPLETION_STATUS]
NORMAL_STATUS = [
    DEPOSIT_WAITING_STATUS, PAYMENT_COMPLETION_STATUS, DELIVERY_PREPARING_STATUS, 
    DELIVERY_PROGRESSING_STATUS, DELIVERY_COMPLETION_STATUS, PURCHASE_CONFIRMATION_STATUS
]

class Order(Model):
    id = BigAutoField(primary_key=True)
    number = CharField(max_length=25, unique=True) 
    shopper = ForeignKey('user.Shopper', DO_NOTHING)
    shipping_address = ForeignKey('ShippingAddress', DO_NOTHING)
    created_at = DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'order'
        ordering = ['-id']

    def __set_default_number(self):
        prefix = self.created_at.strftime(DEFAULT_DATETIME_FORMAT)
        while True:
            postfix = ''.join(random.choices(string.digits, k=5))
            if not self.__class__.objects.filter(number=prefix+postfix).exists():
                self.number = prefix + postfix
                break

    def save(self, *args, **kwargs):
        if kwargs.get('force_insert', False):
            self.__set_default_number()

        return super().save(*args, **kwargs)


class OrderItem(Model):
    id = BigAutoField(primary_key=True)
    order = ForeignKey('Order', DO_NOTHING, related_name='items')
    option = ForeignKey('product.Option', DO_NOTHING)
    status = ForeignKey('Status', DO_NOTHING)
    count = IntegerField(default=1)
    sale_price = IntegerField()
    base_discount_price = IntegerField(default=0)
    membership_discount_price = IntegerField()
    shopper_coupon = ForeignKey('user.ShopperCoupon', DO_NOTHING, null=True)
    coupon_discount_price = IntegerField(default=0)
    used_point = IntegerField(default=0)
    payment_price = IntegerField()
    earned_point = IntegerField()
    delivery = ForeignKey('Delivery', DO_NOTHING, null=True)

    class Meta:
        db_table = 'order_item'
        ordering = ['id']


class Status(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'status'

    def __str__(self):
        return self.name


class StatusHistory(Model):
    id = BigAutoField(primary_key=True)
    order_item = ForeignKey('OrderItem', DO_NOTHING, related_name='status_history')
    status = ForeignKey('Status', DO_NOTHING)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'status_history'
        ordering = ['id']


class ShippingAddress(Model):
    id = BigAutoField(primary_key=True)
    receiver_name = CharField(max_length=20)
    mobile_number = CharField(max_length=11)
    phone_number = CharField(max_length=11, null=True)
    zip_code = CharField(max_length=5)
    base_address = CharField(max_length=200)
    detail_address = CharField(max_length=100)
    shipping_message = CharField(max_length=50)

    class Meta:
        db_table = 'shipping_address'

# todo
# claim (취소, 환불) 설계 및 구현
# 결제, 환불 설계 및 구현

class CancellationInformation(Model):
    order_item = OneToOneField('OrderItem', DO_NOTHING, primary_key=True)
    refund = ForeignKey('Refund', DO_NOTHING, null=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cancellation_information'


class ExchangeInformation(Model):
    order_item = OneToOneField('OrderItem', DO_NOTHING, primary_key=True)
    new_order_item = OneToOneField('OrderItem', DO_NOTHING, related_name='origin_order_item_exchange_information')
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)

    class Meta:
        db_table = 'exchange_information'


class ReturnInformation(Model):
    order_item = OneToOneField('OrderItem', DO_NOTHING, primary_key=True)
    refund = ForeignKey('Refund', DO_NOTHING)
    created_at = DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table = 'return_information'


class Refund(Model):
    id = BigAutoField(primary_key=True)
    price = IntegerField()
    completed_at = DateTimeField(null=True)

    class Meta:
        db_table = 'refund'

    # todo
    # 환불 수단 추가


class StatusTransition(Model):
    id = AutoField(primary_key=True)
    previous_status = ForeignKey('Status', DO_NOTHING, related_name='transition_previous_status')
    next_status = ForeignKey('Status', DO_NOTHING, related_name='transition_next_status')
    
    class Meta:
        db_table = 'status_transition'


class Delivery(Model):
    id = BigAutoField(primary_key=True)
    company = CharField(max_length=20)
    invoice_number = CharField(max_length=30)
    shipping_fee = IntegerField(default=0)
    flag = CharField(max_length=30)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery'
        ordering = ['id']