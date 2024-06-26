from django.db.models import (
    Model, ForeignKey, ManyToManyField, DO_NOTHING, AutoField, CharField, ImageField,  BooleanField, 
    BigAutoField, IntegerField, DateTimeField, Manager
)
from django.db.models.query import QuerySet

from common import storage


class ProductColorQueyset(QuerySet):
    def delete(self):
        for instance in self:
            instance.options.all().update(on_sale=False)

        self.update(on_sale=False)


class ProductColorManager(Manager):
    def get_queryset(self):
        return ProductColorQueyset(self.model, using=self._db)


class MainCategory(Model):
    id = AutoField(primary_key=True)
    name = CharField(unique=True, max_length=20)
    image_url = ImageField(max_length=200, storage=storage.ClientSVGStorage)
    product_additional_information_required = BooleanField(default=True)
    laundry_informations_required = BooleanField(default=True)

    class Meta:
        db_table = 'main_category'
        ordering = ['id']

    def __str__(self):
        return self.name


class SubCategory(Model):
    id = AutoField(primary_key=True)
    main_category = ForeignKey('MainCategory', related_name='sub_categories', on_delete=DO_NOTHING)
    name = CharField(max_length=20)

    class Meta:
        db_table = 'sub_category'

    def __str__(self):
        return self.name


class Product(Model):
    id = BigAutoField(primary_key=True)
    wholesaler = ForeignKey('user.Wholesaler', DO_NOTHING)
    sub_category = ForeignKey('SubCategory', DO_NOTHING)
    style = ForeignKey('common.SettingItem', DO_NOTHING, related_name='product_style')
    target_age_group = ForeignKey('common.SettingItem', DO_NOTHING, related_name='product_target_age_group')
    tags = ManyToManyField('Tag', db_table='product_tag')
    laundry_informations = ManyToManyField('common.SettingItem', through='ProductLaundryInformation', related_name='product_laundry_information')
    name = CharField(max_length=100)
    code = CharField(max_length=12, default='AA')
    created_at = DateTimeField(auto_now_add=True)
    price = IntegerField()
    sale_price = IntegerField()
    base_discount_rate = IntegerField(default=0)
    base_discounted_price = IntegerField()
    on_sale = BooleanField(default=True)
    additional_information = ForeignKey('ProductAdditionalInformation', DO_NOTHING, null=True)
    manufacturing_country = CharField(max_length=20)
    like_shoppers = ManyToManyField('user.Shopper', through='user.ProductLike')

    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.name

    def delete(self):
        self.question_answers.all().delete()
        self.productlike_set.all().delete()
        self.colors.all().update(on_sale=False)
        Option.objects.filter(product_color__product=self).update(on_sale=False)
        self.on_sale = False
        self.save(update_fields=('on_sale',))


class ProductAdditionalInformation(Model):
    id = AutoField(primary_key=True)
    thickness = ForeignKey('common.SettingItem', DO_NOTHING, related_name='product_additional_information_thickness')
    see_through = ForeignKey('common.SettingItem', DO_NOTHING, related_name='product_additional_information_see_through')
    flexibility = ForeignKey('common.SettingItem', DO_NOTHING, related_name='product_additional_information_flexibility')
    lining = ForeignKey('common.SettingItem', DO_NOTHING, related_name='product_additional_information_lining')

    class Meta:
        db_table = 'product_additional_information'


class ProductImage(Model):
    id = BigAutoField(primary_key=True)
    product = ForeignKey('Product', DO_NOTHING, related_name='images')
    image_url = CharField(max_length=200)
    sequence = IntegerField()

    class Meta:
        db_table = 'product_image'
        ordering = ['sequence']


class Tag(Model):
    id = AutoField(primary_key=True)
    name = CharField(unique=True, max_length=20)

    class Meta:
        db_table = 'tag'
        ordering = ['id']

    def __str__(self):
        return self.name


class Color(Model):
    id = AutoField(primary_key=True)
    name = CharField(unique=True, max_length=20)
    default_image_url = ImageField(max_length=200, storage=storage.ClientSVGStorage)
    checked_image_url = ImageField(max_length=200, storage=storage.ClientSVGStorage)

    class Meta:
        db_table = 'color'
        ordering = ['id']

    def __str__(self):
        return self.name


class ProductColor(Model):
    id = AutoField(primary_key=True)
    product = ForeignKey('Product', DO_NOTHING, related_name='colors')
    color = ForeignKey('Color', DO_NOTHING)
    display_color_name = CharField(max_length=20)
    image_url = CharField(max_length=200)
    on_sale = BooleanField(default=True)

    objects = ProductColorManager()

    class Meta:
        db_table = 'product_color'

    def save(self, *args, **kwargs):
        if not self.display_color_name:
            self.display_color_name = self.color.name
        super().save(*args, **kwargs)


class Option(Model):
    id = BigAutoField(primary_key=True)
    product_color = ForeignKey('ProductColor', DO_NOTHING, related_name='options')
    size = ForeignKey('common.SettingItem', DO_NOTHING, related_name='options')
    on_sale = BooleanField(default=True)

    class Meta:
        db_table = 'option'


class Keyword(Model):
    id = AutoField(primary_key=True)
    name = CharField(unique=True, max_length=20)

    class Meta:
        db_table = 'keyword'


class ProductLaundryInformation(Model):
    id = BigAutoField(primary_key=True)
    product = ForeignKey('Product', DO_NOTHING)
    laundry_information = ForeignKey('common.SettingItem', DO_NOTHING)  

    class Meta:
        db_table = 'product_laundry_information'
        unique_together = (('product', 'laundry_information'),)


class ProductMaterial(Model):
    id = AutoField(primary_key=True)
    product = ForeignKey('Product', DO_NOTHING, related_name='materials')
    material = CharField(max_length=20)
    mixing_rate = IntegerField()

    class Meta:
        db_table = 'product_material'


class ProductQuestionAnswerClassification(Model):
    id = AutoField(primary_key=True)
    name = CharField(unique=True, max_length=20)

    class Meta:
        db_table = 'product_question_answer_classification'
        ordering = ['id']

    def __str__(self):
        return self.name


class ProductQuestionAnswer(Model):
    id = AutoField(primary_key=True)
    product = ForeignKey('Product', DO_NOTHING, related_name='question_answers')
    shopper = ForeignKey('user.Shopper', DO_NOTHING, related_name='question_answers')
    classification = ForeignKey('ProductQuestionAnswerClassification', DO_NOTHING)
    created_at = DateTimeField(auto_now_add=True)
    question = CharField(max_length=1000)
    answer = CharField(max_length=1000)
    is_secret = BooleanField(default=False)

    class Meta:
        db_table = 'product_question_answer'
        ordering = ['-created_at']
