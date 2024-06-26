import string, random

from django.utils import timezone

from factory import Sequence, LazyAttribute, SubFactory, Faker, LazyFunction, lazy_attribute

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from common.test.factories import SettingGroupFactory, SettingItemFactory
from common.utils import IMAGE_DATETIME_FORMAT
from user.test.factories import WholesalerFactory, ShopperFactory


def create_options(size=2, only_product_color=False):
    size_group = SettingGroupFactory(main_key='sizes')
    option = OptionFactory(size__group=size_group)
    

    if only_product_color:
        return [option] + [OptionFactory(product_color=option.product_color, size__group=size_group) for _ in range(size-1)]
    else:
        return [option] + [OptionFactory(product_color__product=ProductFactory(product=option.product_color.product), size__group=size_group) for _ in range(size-1)]


def create_product_additional_information(for_validation=False):
    sub_keys = ['thickness', 'see_through', 'flexibility', 'lining']
    if for_validation:
        setting_items = {sub_key: SettingItemFactory(group__main_key='additional_information', group__sub_key=sub_key) for sub_key in sub_keys}
    else:
        setting_group = SettingGroupFactory()
        setting_items = {sub_key: SettingItemFactory(group=setting_group) for sub_key in sub_keys}

    return ProductAdditionalInformationFactory(**setting_items)


class MainCategoryFactory(DjangoModelFactory):
    class Meta:
        model = 'product.MainCategory'

    name = Sequence(lambda num: 'main_category_{0}'.format(num))
    image_url = LazyAttribute(lambda obj: 'category/{0}.svg'.format(obj.name))


class SubCategoryFactory(DjangoModelFactory):
    class Meta:
        model = 'product.SubCategory'

    main_category = SubFactory(MainCategoryFactory)
    name = Sequence(lambda num: 'sub_category_{0}'.format(num))
    # require_product_additional_information = True
    # require_laundry_information = True


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = 'product.Product'

    wholesaler = SubFactory(WholesalerFactory)
    sub_category = SubFactory(SubCategoryFactory)
    style = SubFactory(SettingItemFactory, group__main_key='style')
    target_age_group = SubFactory(SettingItemFactory, group__main_key='target_age_group')
    name = Sequence(lambda num: 'product_{0}'.format(num))
    price = FuzzyInteger(10000, 5000000, 100)
    sale_price = LazyAttribute(lambda obj: obj.price * 2)
    base_discount_rate = FuzzyInteger(0, 50)
    base_discounted_price = LazyAttribute(lambda obj: obj.sale_price - int(obj.sale_price * obj.base_discount_rate / 100) // 100 * 100)
    manufacturing_country = Faker('country', locale='ko-KR')
        
    @classmethod
    def _generate(cls, strategy, params):
        if 'product' in params:
            product = params.pop('product')
            copy_fields = ['wholesaler', 'sub_category', 'style', 'target_age_group', 'additional_information']
            for field in copy_fields:
                if field not in params:
                    params[field] = getattr(product, field, None)

        return super()._generate(strategy, params)


class ProductAdditionalInformationFactory(DjangoModelFactory):
    class Meta:
        model = 'product.ProductAdditionalInformation'

    thickness = SubFactory('common.test.factories.SettingItemFactory')
    see_through = SubFactory('common.test.factories.SettingItemFactory')
    flexibility = SubFactory('common.test.factories.SettingItemFactory')
    lining = SubFactory('common.test.factories.SettingItemFactory')


class TagFactory(DjangoModelFactory):
    class Meta:
        model = 'product.Tag'

    name = Sequence(lambda num: 'tag_{0}'.format(num))


class ColorFactory(DjangoModelFactory):
    class Meta:
        model = 'product.Color'

    name = Sequence(lambda num: 'color_{0}'.format(num))
    default_image_url = LazyAttribute(lambda obj: f'color/{obj.name}.svg')
    checked_image_url = LazyAttribute(lambda obj: f'color/check_{obj.name}.svg')


class ProductColorFactory(DjangoModelFactory):
    class Meta:
        model = 'product.ProductColor'

    product = SubFactory(ProductFactory)
    color = SubFactory(ColorFactory)
    image_url = LazyFunction(lambda: '{}.jpeg'.format(timezone.now().strftime(IMAGE_DATETIME_FORMAT)))
    display_color_name = Sequence(lambda num: 'dp_name_{0}'.format(num))

    @classmethod
    def _generate(cls, strategy, params):
        if 'product_color' in params:
            product_color = params.pop('product_color')
            copy_fields = ['product', 'color']
            for field in copy_fields:
                if field not in params:
                    params[field] = getattr(product_color, field, None)

        return super()._generate(strategy, params)


class OptionFactory(DjangoModelFactory):
    class Meta:
        model = 'product.option'

    product_color = SubFactory(ProductColorFactory)
    size = SubFactory(SettingItemFactory, group__main_key='sizes')


class ProductMaterialFactory(DjangoModelFactory):
    class Meta:
        model = 'product.ProductMaterial'

    product = SubFactory(ProductFactory)
    mixing_rate = 100

    @lazy_attribute
    def material(self):
        string_length = 10
        return ''.join(random.sample(string.ascii_letters, string_length))


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = 'product.ProductImage'

    product = SubFactory(ProductFactory)
    image_url = LazyFunction(lambda: '{}.jpeg'.format(timezone.now().strftime(IMAGE_DATETIME_FORMAT)))
    sequence = Sequence(lambda num: num)


class KeyWordFactory(DjangoModelFactory):
    class Meta:
        model = 'product.Keyword'

    name = Sequence(lambda num: 'keyword_{0}'.format(num))


class ProductQuestionAnswerClassificationFactory(DjangoModelFactory):
    class Meta:
        model = 'product.ProductQuestionAnswerClassification'

    name = Sequence(lambda num: 'classification_{0}'.format(num))


class ProductQuestionAnswerFactory(DjangoModelFactory):
    class Meta:
        model = 'product.ProductQuestionAnswer'

    product = SubFactory(ProductFactory)
    shopper = SubFactory(ShopperFactory)
    classification = SubFactory(ProductQuestionAnswerClassificationFactory)
    question = Faker('sentence')
    answer = Faker('sentence')
    is_secret = Faker('pybool')
