import random, copy

from django.db.models.query import Prefetch
from django.db.models import Count
from django.forms import model_to_dict

from rest_framework.exceptions import ValidationError

from factory import RelatedFactoryList

from common.models import TemporaryImage, SettingGroup
from common.serializers import SettingItemSerializer, SettingGroupSerializer
from common.utils import DEFAULT_IMAGE_URL, BASE_IMAGE_URL, datetime_to_iso, get_full_image_url
from common.test.test_cases import SerializerTestCase, ListSerializerTestCase
from common.test.factories import SettingItemFactory, SettingGroupFactory
from common.test.test_serializers import  get_setting_groups_test_data
from user.test.factories import WholesalerFactory, ShopperFactory
from user.models import ProductLike
from .factories import (
    ProductColorFactory, ProductFactory, SubCategoryFactory, MainCategoryFactory, ColorFactory, 
    TagFactory, ProductImageFactory, ProductMaterialFactory, OptionFactory, ProductQuestionAnswerFactory, 
    ProductQuestionAnswerClassificationFactory,
    create_product_additional_information,
)
from ..serializers import (
    ProductMaterialSerializer, SubCategorySerializer, MainCategorySerializer, ColorSerializer,
    ProductColorSerializer, ProductColorWriteSerializer, ProductImageSerializer, OptionSerializer, OptionWriteSerializer, ProductSerializer, ProductReadSerializer, 
    ProductWriteSerializer, TagSerializer, ProductQuestionAnswerSerializer, ProductQuestionAnswerClassificationSerializer, 
    OptionInOrderItemSerializer, ProductAdditionalInformationSerializer, ProductAdditionalInformationWriteSerializer, 
    ProductRegistrationSerializer,
    PRODUCT_IMAGE_MAX_LENGTH, PRODUCT_COLOR_MAX_LENGTH,
)
from ..models import Product, ProductColor, Color, Option, ProductMaterial, ProductQuestionAnswer


def get_product_registration_test_data(setting_group_kwargs={}):
    get_setting_groups_test_data(**setting_group_kwargs)
    
    return {
        'main_categories': [MainCategoryFactory(sub_categoies=RelatedFactoryList(SubCategoryFactory, 'main_category'))],
        'colors': ColorFactory.create_batch(2),
        'setting_groups': SettingGroup.objects.prefetch_related('items').all(),
    }


class SubCategorySerializerTestCase(SerializerTestCase):
    _serializer_class = SubCategorySerializer

    def test_model_instance_serialization(self):
        sub_category = SubCategoryFactory()
        expected_data = {
            'id': sub_category.id,
            'name': sub_category.name,
        }

        self._test_model_instance_serialization(sub_category, expected_data)


class MainCategorySerializerTestCase(SerializerTestCase):
    _serializer_class = MainCategorySerializer

    def test_model_instance_serialization(self):
        main_category = MainCategoryFactory()
        SubCategoryFactory.create_batch(3, main_category=main_category)
        expected_data = {
            'id': main_category.id,
            'name': main_category.name,
            'image_url': main_category.image_url.url,
            'sub_categories': [
                {'id': sub_category.id, 'name': sub_category.name} 
                for sub_category in main_category.sub_categories.all()
            ],
            'product_additional_information_required': True,
            'laundry_informations_required': True,
        }

        self._test_model_instance_serialization(main_category, expected_data)


class ColorSerializerTestCase(SerializerTestCase):
    _serializer_class = ColorSerializer

    def test_model_instance_serialization(self):
        color = ColorFactory()
        expected_data = {
            'id': color.id,
            'name': color.name,
            'default_image_url': color.default_image_url.url,
        }

        self._test_model_instance_serialization(color, expected_data)


class ProductAdditionalInformationSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductAdditionalInformationSerializer

    def test_model_instance_serialization(self):
        product_additional_information = create_product_additional_information()

        self._test_model_instance_serialization(product_additional_information, {
            'thickness': SettingItemSerializer(product_additional_information.thickness).data,
            'see_through': SettingItemSerializer(product_additional_information.see_through).data,
            'flexibility': SettingItemSerializer(product_additional_information.flexibility).data,
            'lining': SettingItemSerializer(product_additional_information.lining).data,
        })


class ProductAdditionalInformationWriteSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductAdditionalInformationWriteSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__product_additional_information = create_product_additional_information(True)

        cls._test_data = {
            'thickness': cls.__product_additional_information.thickness.id,
            'see_through': cls.__product_additional_information.see_through.id,
            'flexibility': cls.__product_additional_information.flexibility.id,
            'lining': cls.__product_additional_information.lining.id,
        }

    def test_validation_success(self):
        self.assertTrue(self._get_serializer_after_validation())

    def test_validate(self):
        self._test_data['see_through'] = self._test_data['thickness']
        self._test_data['lining'] = self._test_data['flexibility']

        self._test_serializer_raise_validation_error('of additional_information is invalid.')

    def test_create_with_existing_data(self):
        product_additional_information = self._get_serializer().create(self._test_data)

        self.assertEqual(product_additional_information, self.__product_additional_information)

    def test_create(self):
        self._test_data['thickness'] = SettingItemFactory(group=self.__product_additional_information.thickness.group).id
        product_additional_information = self._get_serializer().create(self._test_data)

        self.assertTrue(product_additional_information != self.__product_additional_information)


class TagSerializerTestCase(SerializerTestCase):
    _serializer_class = TagSerializer

    def test_model_instance_serialization(self):
        tag = TagFactory()
        expected_data = {
            'id': tag.id,
            'name': tag.name,
        }

        self._test_model_instance_serialization(tag, expected_data)


class ProductImageSerializerTestCase(SerializerTestCase):
    fixtures = ['temporary_image']
    _serializer_class = ProductImageSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__image_url = TemporaryImage.objects.first().image_url
        cls.__product_image = ProductImageFactory()
        cls._data = {
            'image_url': get_full_image_url(cls.__image_url),
            'sequence': 1,
        }

    def test_model_instance_serialization(self):

        expected_data = {
            'id': self.__product_image.id,
            'image_url': get_full_image_url(self.__product_image.image_url),
            'sequence': self.__product_image.sequence,
        }

        self._test_model_instance_serialization(self.__product_image, expected_data)

    def _test_validated_data(self):
        expected_validated_data = {
            'image_url': self.__image_url,
            'sequence': self._data['sequence']
        }

        self._test_validated_data(expected_validated_data, data=self._data)

    def test_raise_validation_error_create_data_does_not_include_all_required_field_in_update(self):
        key = random.choice(list(self._data.keys()))
        self._data.pop(key)

        expected_message = '{0} field is required.'.format(key)
        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_image, data=self._data, partial=True
        )

    def test_raise_validation_error_update_image_url(self):
        data = {
            'id': self.__product_image.id,
            'image_url': get_full_image_url(TemporaryImage.objects.last().image_url),
            'sequence': 1,
        }

        expected_message = 'Image url data cannot be updated.'
        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_image, data=data, partial=True
        )


class ProductImageListSerializerTestCase(ListSerializerTestCase):
    fixtures = ['temporary_image']
    _child_serializer_class = ProductImageSerializer
    __batch_size = 2

    @classmethod
    def setUpTestData(cls):
        cls.__temporary_images = TemporaryImage.objects.all().values_list('image_url', flat=True)
        cls.__data = [
            {
                'image_url': get_full_image_url(cls.__temporary_images[i]),
                'sequence': i+1,
            } for i in range(cls.__batch_size)
        ]
        cls.__product = ProductFactory()
        cls.__images = ProductImageFactory.create_batch(size=cls.__batch_size, product=cls.__product)

    def test_create(self):
        serializer = self._get_serializer()
        serializer.create(self.__data, self.__product)
        
        exclude_id_list = [image.id for image in self.__images]
        created_images = self.__product.images.exclude(id__in=exclude_id_list)

        self.assertListEqual(
            [{'image_url': image.image_url, 'sequence': image.sequence} for image in created_images],
            [{'image_url': data['image_url'], 'sequence': data['sequence']} for data in self.__data]
        )

    def test_update_create_data(self):
        serializer = self._get_serializer()
        serializer.update(self.__data, self.__product)

        exclude_id_list = [image.id for image in self.__images]
        created_images = self.__product.images.exclude(id__in=exclude_id_list)

        self.assertListEqual(
            [{'image_url': image.image_url, 'sequence': image.sequence} for image in created_images],
            [{'image_url': data['image_url'], 'sequence': data['sequence']} for data in self.__data]
        )

    def test_update_update_data(self):
        updating_image = self.__images[0]
        data = [{
            'id': updating_image.id,
            'sequence': updating_image.sequence + 1,
        }]

        serializer = self._get_serializer()
        serializer.update(data, self.__product)

        updated_image = self.__product.images.get(id=updating_image.id)

        self.assertListEqual(
            data, [model_to_dict(updated_image, fields=['id', 'sequence'])]
        )

    def test_update_delete_data(self):
        delete_id = self.__images[-1].id
        data = [{'id': delete_id}]

        serializer = self._get_serializer()
        serializer.update(data, self.__product)

        self.assertTrue(not self.__product.images.filter(id=delete_id).exists())

    def test_validate_image_number_in_create(self):
        data = [{} for _ in range(PRODUCT_COLOR_MAX_LENGTH + 1)]

        self.assertRaisesMessage(
            ValidationError,
            'The product cannot have more than ten images.',
            self._get_serializer().validate,
            data
        )

    def test_validate_image_number_in_update_number_more_than_max(self):
        self.__data += [
            {
                'image_url': get_full_image_url(self.__temporary_images[i]),
                'sequence': i+1,
            } for i in range(len(self.__images), PRODUCT_IMAGE_MAX_LENGTH + len(self.__images) + 1)
        ]
        self.__data += [{'id': image.id} for image in self.__images]

        self.assertRaisesMessage(
            ValidationError,
            'The product cannot have more than ten images.',
            self._get_serializer(instance=self.__product, partial=True).validate,
            self.__data
        )

    def test_validate_image_number_in_update_number_delete_all_images(self):
        data = [{'id': image.id} for image in self.__images]

        self.assertRaisesMessage(
            ValidationError,
            'The product must have at least one image.',
            self._get_serializer(instance=self.__product, partial=True).validate,
            data
        )

    def test_validate_sequence_sequences_not_startswith_one_in_create(self):
        for data in self.__data:
            data['sequence'] += 1

        self.assertRaisesMessage(
            ValidationError,
            'The sequence of the images must be ascending from 1 to n.',
            self._get_serializer(instance=self.__product, partial=True).validate,
            self.__data
        )

    def test_raise_validation_error_duplicated_sequences_in_create(self):
        self.__data[0]['sequence'] = self.__data[-1]['sequence']

        self.assertRaisesMessage(
            ValidationError,
            'The sequence of the images must be ascending from 1 to n.',
            self._get_serializer(instance=self.__product).validate,
            self.__data
        )

    def test_raise_validation_error_omitted_sequences_in_create(self):
        self.__data[-1]['sequence'] += 1

        self.assertRaisesMessage(
            ValidationError,
            'The sequence of the images must be ascending from 1 to n.',
            self._get_serializer(instance=self.__product).validate,
            self.__data
        )

    def test_raise_validation_error_duplicated_sequences_in_update(self):
        data = [{
            'id': self.__images[0].id,
            'sequence': self.__images[-1].sequence + 1,
        }]

        self.assertRaisesMessage(
            ValidationError,
            'The sequence of the images must be ascending from 1 to n.',
            self._get_serializer(instance=self.__product).validate,
            data
        )

    def test_raise_validation_error_duplicated_sequences_in_update(self):
        data = [{
                'image_url': get_full_image_url(self.__temporary_images[0]), 
                'sequence': self.__product.images.last().sequence,
            }]

        self.assertRaisesMessage(
            ValidationError,
            'The sequence of the images must be ascending from 1 to n.',
            self._get_serializer(instance=self.__product).validate,
            data
        )

    def test_raise_validation_error_omitted_sequences_in_update(self):
        data = [{
                'image_url': get_full_image_url(self.__temporary_images[0]),
                'sequence': self.__product.images.last().sequence + 2,
            }]

        self.assertRaisesMessage(
            ValidationError,
            'The sequence of the images must be ascending from 1 to n.',
            self._get_serializer(instance=self.__product).validate,
            data
        )


class ProductMaterialSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductMaterialSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__product = ProductFactory()
        cls.__product_material = ProductMaterialFactory(product=cls.__product)
        cls.__data = {
            'material': '가죽',
            'mixing_rate': 100,
        }

    def test_model_instance_serialization(self):
        expected_data = {
            'id': self.__product_material.id,
            'material': self.__product_material.material,
            'mixing_rate': self.__product_material.mixing_rate,
        }

        self._test_model_instance_serialization(self.__product_material, expected_data)

    def test_raise_validation_error_create_data_does_not_include_all_required_field_in_update(self):
        key = random.choice(list(self.__data.keys()))
        self.__data.pop(key)
        expected_message = '{0} field is required.'.format(key)

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_material, data=self.__data, partial=True
        )


class ProductMaterialListSerializerTestCase(ListSerializerTestCase):
    _child_serializer_class = ProductMaterialSerializer
    __material_num = 2

    @classmethod
    def setUpTestData(cls):
        cls.__product = ProductFactory()
        cls.__materials = ProductMaterialFactory.create_batch(
            cls.__material_num, product=cls.__product, mixing_rate=50
        )
        cls.__create_data = [
            {
                'material': cls.__materials[i].material,
                'mixing_rate': 50,
            }for i in range(cls.__material_num)
        ]
        cls.__update_data = [
            {
                'id': cls.__materials[i].id,
                'material': cls.__materials[i].material,
                'mixing_rate': 50,
            }for i in range(cls.__material_num)
        ]

    def test_create(self):
        serializer = self._get_serializer()
        serializer.create(self.__create_data, self.__product)

        exclude_id_list = [material.id for material in self.__materials]
        created_materials = self.__product.materials.exclude(id__in=exclude_id_list)

        self.assertListEqual(
            [{'material': material.material, 'mixing_rate': material.mixing_rate} for material in created_materials],
            [{'material': data['material'], 'mixing_rate': data['mixing_rate']} for data in self.__create_data]
        )

    def test_update_create_data(self):
        serializer = self._get_serializer()
        serializer.update(self.__create_data, self.__product)

        exclude_id_list = [material.id for material in self.__materials]
        created_materials = self.__product.materials.exclude(id__in=exclude_id_list)

        self.assertListEqual(
            [{'material': material.material, 'mixing_rate': material.mixing_rate} for material in created_materials],
            [{'material': data['material'], 'mixing_rate': data['mixing_rate']} for data in self.__create_data]
        )

    def test_update_update_data(self):
        updating_material = self.__materials[0]
        data = [{
            'id': updating_material.id,
            'material': updating_material.material + 'update',
            'mixing_rate': updating_material.mixing_rate + 10,
        }]

        serializer = self._get_serializer()
        serializer.update(data, self.__product)

        updated_material = self.__product.materials.get(id=updating_material.id)

        self.assertListEqual(
            data,
            [model_to_dict(updated_material, fields=['id', 'material', 'mixing_rate'])]
        )

    def test_update_delete_data(self):
        delete_id = self.__materials[-1].id
        data = [{'id': delete_id}]

        serializer = self._get_serializer()
        serializer.update(data, self.__product)

        self.assertTrue(not self.__product.materials.filter(id=delete_id).exists())

    def test_validate_total_mixing_rates_in_create(self):
        self.__create_data[0]['mixing_rate'] += 10

        self.assertRaisesMessage(
            ValidationError,
            'The total of material mixing rates must be 100.',
            self._get_serializer().validate,
            self.__create_data
        )

    def test_validate_total_mixing_rates_in_update(self):
        self.__update_data[0] = {'id': self.__update_data[0]['id']}
        self.__update_data.pop(-1)
        self.__update_data.append({
            'material': 'material',
            'mixing_rate': 60,
        })

        self.assertRaisesMessage(
            ValidationError,
            'The total of material mixing rates must be 100.',
            self._get_serializer(instance=self.__product).validate,
            self.__update_data
        )

    def test_validate_material_is_duplicated(self):
        self.__create_data[0]['material'] = self.__create_data[-1]['material']

        self.assertRaisesMessage(
            ValidationError,
            'Material is duplicated.',
            self._get_serializer(instance=self.__product).validate,
            self.__create_data
        )

    def test_validate_material_name_uniqueness(self):
        data = [{
            'id': self.__materials[0].id,
            'mixing_rate': self.__materials[0].mixing_rate - 10,
        },
        {
            'material': self.__materials[0].material,
            'mixing_rate': 10,
        }]

        self.assertRaisesMessage(
            ValidationError,
            'The product with the material already exists.',
            self._get_serializer(instance=self.__product).validate,
            data
        )

    def test_delete_and_create_material_name(self):
        data = [
            {
                'material': self.__materials[0].material,
                'mixing_rate': self.__materials[0].mixing_rate,
            },
            {
                'id': self.__materials[0].id,
            }
        ]

        self.assertEqual(
            data, self._get_serializer(instance=self.__product).validate(data)
        )

    def test_exchange_material_name(self):
        material1 = self.__materials[0]
        material2 = self.__materials[1]
        data = [{
            'id': material1.id,
            'material': material2.material,
        },
        {
            'id': material2.id,
            'material': material1.material,
        }
        ]

        self.assertEqual(
            data,
            self._get_serializer(instance=self.__product).validate(data)
        )


class OptionSerializerTestCase(SerializerTestCase):
    _serializer_class = OptionSerializer

    def test_model_instance_serialization(self):
        option = OptionFactory()

        self._test_model_instance_serialization(option, {
            'id': option.id,
            'size': SettingItemSerializer(option.size).data,
            'on_sale': option.on_sale,
        })


class OptionWriteSerializerTestCase(SerializerTestCase):
    _serializer_class = OptionWriteSerializer

    def test_raise_validation_error_update_size_data(self):
        option = OptionFactory()
        self._test_data = {
            'id': option.id,
            'size': SettingItemFactory(group=option.size.group).id,
        }

        self._test_serializer_raise_validation_error('Size data cannot be updated.', option, partial=True)


class OptionListSerializerTestCase(ListSerializerTestCase):
    _child_serializer_class = OptionWriteSerializer
    __option_num = 3

    @classmethod
    def setUpTestData(cls):
        cls.__product_color = ProductColorFactory()
        size_group = SettingGroupFactory(main_key='sizes')
        cls.__options = OptionFactory.create_batch(size=cls.__option_num, product_color=cls.__product_color, size__group=size_group)
        cls._test_data = [{'size': SettingItemFactory(group=size_group)} for _ in range(cls.__option_num)]

    def __call_update(self, data):
        serializer = self._get_serializer()
        serializer.update(data, self.__product_color)

    def test_validate_sizes(self):
        self._test_serializer_raise_validation_error('Size is duplicated.', data=[{'size': self._test_data[0]['size'].id} for _ in range(2)])
    
    def test_create(self):
        serializer = self._get_serializer()
        serializer.create(self._test_data, self.__product_color)
        created_options = self.__product_color.options.exclude(id__in=[option.id for option in self.__options])

        self.assertListEqual([{'size': option.size} for option in created_options], self._test_data)

    def test_create_using_update(self):
        self.__call_update(self._test_data)
        created_options = self.__product_color.options.exclude(id__in=[option.id for option in self.__options])

        self.assertListEqual([{'size': option.size} for option in created_options], self._test_data)

    def test_update(self):
        update_option_id = self.__options[0].id
        data = [{'id': update_option_id, 'size': self._test_data[0]['size']}]
        self.__call_update(data)

        self.assertEqual(self.__product_color.options.get(id=update_option_id).size, data[0]['size'])

    def test_delete_using_update(self):
        delete_option_id = self.__options[-1].id
        self.__call_update([{'id': delete_option_id}])

        self.assertEqual(self.__product_color.options.get(id=delete_option_id).on_sale, False)


class OptionInOrderItemSerializerTestCase(SerializerTestCase):
    _serializer_class = OptionInOrderItemSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__option = OptionFactory()
        cls.__expected_data = {
            'id': cls.__option.id,
            'size': cls.__option.size.name,
            'display_color_name': cls.__option.product_color.display_color_name,
            'product_id': cls.__option.product_color.product.id,
            'product_name': cls.__option.product_color.product.name,
            'product_code': cls.__option.product_color.product.code,
        }

    def test_model_instance_serialization_with_image(self):
        img = ProductImageFactory(product=self.__option.product_color.product)
        self.__expected_data['product_image_url'] = get_full_image_url(img.image_url)

        self._test_model_instance_serialization(self.__option, self.__expected_data)

    def test_model_instance_serialization_without_image(self):
        self.__expected_data['product_image_url'] = DEFAULT_IMAGE_URL

        self._test_model_instance_serialization(self.__option, self.__expected_data)


class ProductColorSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductColorSerializer

    def test_model_instance_serialization(self):
        product_color = ProductColorFactory()
        option = OptionFactory.create(product_color=product_color)

        self._test_model_instance_serialization(product_color, {
            'id': product_color.id,
            'color': product_color.color.id,
            'display_color_name': product_color.display_color_name,
            'options': OptionSerializer([option], many=True).data,
            'image_url': get_full_image_url(product_color.image_url),
            'on_sale': product_color.on_sale,
        })


class ProductColorWriteSerializerTestCase(SerializerTestCase):
    fixtures = ['temporary_image']
    _serializer_class = ProductColorWriteSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__product_color = ProductColorFactory()
        size_group = SettingGroupFactory(main_key='sizes')
        cls.__options = OptionFactory.create_batch(size=3, product_color=cls.__product_color, size__group=size_group)
        cls.data = {
            'display_color_name': 'deepblue',
            'color': cls.__product_color.color.id,
            'options': [{'size': option.size_id} for option in cls.__options],
            'image_url': get_full_image_url(TemporaryImage.objects.first().image_url),
        }
        cls._test_data = cls.data

    def test_raise_validation_error_update_color_data(self):
        color = ColorFactory()
        self.data['id'] = self.__product_color.id
        self.data['color'] = color.id
        expected_message = 'Color data cannot be updated.'

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_color, data=self.data, partial=True
        )

    def test_raise_validation_error_create_data_not_include_all_required_field_in_partial(self):
        key = random.choice(list(self.data.keys()))
        self.data.pop(key)
        expected_message = '{0} field is required.'.format(key)

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_color, data=self.data, partial=True
        )

    def test_raise_validation_error_update_non_unique_size_in_partial(self):
        self.data['id'] = self.__product_color.id
        new_option_data = {'size': self.__options[1].size_id}
        self.data['options'] = [new_option_data]
        expected_message = 'The option with the size already exists.'

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_color, data=self.data, partial=True
        )

    def test_raise_validation_error_delete_all_options(self):
        data = {
            'id': self.__product_color.id,
            'options': [
                {'id': option.id}
                for option in self.__options
            ]
        }
        expected_message = 'The product color must have at least one option.'

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product_color, data=data, partial=True
        )


class ProductColorListSerializerTestCase(ListSerializerTestCase):
    fixtures = ['temporary_image']
    _child_serializer_class = ProductColorWriteSerializer
    __batch_size = 2

    @classmethod
    def setUpTestData(cls):
        cls.__color = ColorFactory()
        cls.__temporary_images = list(TemporaryImage.objects.all().values_list('image_url', flat=True))
        cls.__product = ProductFactory()
        cls.__product_colors = [
            ProductColorFactory(product=cls.__product, image_url=cls.__temporary_images[i], color=cls.__color)
            for i in range(cls.__batch_size)
        ]
        size_group = SettingGroupFactory(main_key='sizes')
        for product_color in cls.__product_colors:
            OptionFactory(product_color=product_color, size__group=size_group)

        cls.__data = [{
            'display_color_name': cls.__color.name,
            'color': cls.__color,
            'options': [{
                'size': SettingItemFactory(group=size_group),
            }],
            'image_url': get_full_image_url(cls.__temporary_images[0])
        }]

    def test_create(self):
        serializer = self._get_serializer()
        serializer.create(copy.deepcopy(self.__data), self.__product)

        exclude_id_list = [product_color.id for product_color in self.__product_colors]
        created_product_colors = self.__product.colors.exclude(id__in=exclude_id_list)

        self.assertListEqual(
            [{
                'display_color_name': color.display_color_name,
                'color': color.color,
                'options': [{'size': option.size} for option in color.options.all()],
                'image_url': color.image_url,
            } for color in created_product_colors],
            self.__data
        )

    def test_update_create_data(self):
        serializer = self._get_serializer()
        serializer.update(copy.deepcopy(self.__data), self.__product)

        exclude_id_list = [product_color.id for product_color in self.__product_colors]
        created_product_colors = self.__product.colors.exclude(id__in=exclude_id_list)

        self.assertListEqual(
            [{
                'display_color_name': color.display_color_name,
                'color': color.color,
                'options': [{'size': option.size} for option in color.options.all()],
                'image_url': color.image_url,
            }for color in created_product_colors],
            self.__data
        )

    def test_update_update_data(self):
        updating_product_color = self.__product_colors[0]
        data = [{
            'id': updating_product_color.id,
            'display_color_name': updating_product_color.display_color_name + 'update',
            'color': ColorFactory(),
            'image_url': updating_product_color.image_url + 'update',
        }]

        serializer = self._get_serializer()
        serializer.update(data, self.__product)

        updated_product_color = self.__product.colors.get(id=updating_product_color.id)

        self.assertListEqual(
            [{
                'id': updated_product_color.id,
                'display_color_name': updated_product_color.display_color_name,
                'color': updated_product_color.color,
                'image_url': updated_product_color.image_url,
            }],
            data
        )

    def test_update_delete_data(self):
        delete_id = self.__product_colors[-1].id
        data = [{'id': delete_id}]

        serializer = self._get_serializer()
        serializer.update(data, self.__product)

        self.assertTrue(not self.__product.colors.filter(id=delete_id, on_sale=True).exists())

    def test_validate_color_length_in_create(self):
        data = [{} for _ in range(11)]

        self.assertRaisesMessage(
            ValidationError,
            'The product cannot have more than ten colors.',
            self._get_serializer().validate,
            data
        )

    def test_validate_color_length_in_update_more_than_max_length(self):
        create_data = [
            {
                'display_color_name': 'display_name{0}'.format(i),
                'color': self.__color.id,
            }
            for i in range(PRODUCT_COLOR_MAX_LENGTH + 1)
        ]
        delete_data = list(self.__product.colors.all().values('id'))
        
        self.assertRaisesMessage(
            ValidationError,
            'The product cannot have more than ten colors.',
            self._get_serializer(instance=self.__product).validate,
            create_data + delete_data
        )

    def test_validate_color_length_in_update_delete_all_colors(self):
        data = list(self.__product.colors.all().values('id'))

        self.assertRaisesMessage(
            ValidationError,
            'The product must have at least one color.',
            self._get_serializer(instance=self.__product).validate,
            data
        )

    def test_validate_display_color_name_is_duplicated(self):
        data = [
            {'display_color_name': 'display'},
            {'display_color_name': 'display'},
            {'display_color_name': 'display_1'}
        ]

        self.assertRaisesMessage(
            ValidationError,
            'display_color_name is duplicated.',
            self._get_serializer().validate,
            data
        )

    def test_validate_display_color_name_uniqueness(self):
        data = [{
            'display_color_name': self.__product.colors.first().display_color_name,
            'color': self.__color.id,
        }]

        self.assertRaisesMessage(
            ValidationError,
            'The product with the display_color_name already exists.',
            self._get_serializer(instance=self.__product).validate,
            data
        )

    def test_delete_and_create_display_color_name(self):
        data = [{
            'display_color_name': self.__product_colors[0].display_color_name,
            'color': self.__color.id,
        },
        {
            'id': self.__product_colors[0].id,
        }]

        self.assertEqual(
            data, self._get_serializer(instance=self.__product).validate(data)
        )

    def test_exchange_display_color_name(self):
        color1 = self.__product_colors[0]
        color2 = self.__product_colors[1]
        data = [
            {
                'id': color1.id,
                'display_color_name': color2.display_color_name,
            },
            {
                'id': color2.id,
                'display_color_name': color1.display_color_name,
            },
        ]

        self.assertEqual(
            data, self._get_serializer(instance=self.__product).validate(data)
        )

    def test_create_display_color_name_on_sale_false(self):
        self.__product_colors[0].on_sale = False
        self.__product_colors[0].save()
        data = [{
            'id': self.__product_colors[1].id,
            'display_color_name': self.__product_colors[0].display_color_name,
        }]

        self.assertEqual(
            data, self._get_serializer(instance=self.__product).validate(data)
        )


class ProductSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__product = ProductFactory()

    def test_sort_dictionary_by_field_name(self):
        fields = list(self._get_serializer().get_fields().keys())
        random.shuffle(fields)

        prefetch_images = Prefetch('images', to_attr='related_images')
        product = Product.objects.prefetch_related(prefetch_images).get(id=self.__product.id)
        serializer = self._get_serializer(product, context={'field_order': fields})

        self.assertListEqual(list(serializer.data.keys()), fields)


class ProductReadSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductReadSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__product = ProductFactory()
        ProductMaterialFactory(product=cls.__product)
        ProductColorFactory(product=cls.__product)
        ProductImageFactory.create_batch(size=3, product=cls.__product)
        laundry_informations = SettingItemFactory.create_batch(size=3, group=SettingGroupFactory())
        tags = TagFactory.create_batch(size=3)
        cls.__product.laundry_informations.add(*laundry_informations)
        cls.__product.tags.add(*tags)

    def __get_expected_data(self, product):
        expected_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'sale_price': product.sale_price,
            'base_discount_rate': product.base_discount_rate,
            'base_discounted_price': product.base_discounted_price,
            'materials': ProductMaterialSerializer(product.materials.all(), many=True).data,
            'colors': ProductColorSerializer(product.colors.all(), many=True).data,
            'images': ProductImageSerializer(product.images.all(), many=True).data,
            'manufacturing_country': product.manufacturing_country,
            'main_category': MainCategorySerializer(
                product.sub_category.main_category, exclude_fields=('sub_categories',)
                ).data,
            'sub_category': SubCategorySerializer(product.sub_category).data,
            'style': SettingItemSerializer(product.style).data,
            'target_age_group': SettingItemSerializer(product.target_age_group).data,
            'tags': TagSerializer(product.tags.all(), many=True).data,
            'laundry_informations': SettingItemSerializer(product.laundry_informations.all(), many=True).data,
            'created_at': datetime_to_iso(product.created_at),
            'on_sale': product.on_sale,
            'code': product.code,
            'total_like': product.like_shoppers.all().count(),
        }

        return expected_data

    def test_model_instance_serialization_detail(self):
        expected_data = self.__get_expected_data(self.__product)
        expected_data['shopper_like'] = False
        prefetch_images = Prefetch('images', to_attr='related_images')
        product = Product.objects.prefetch_related(
                    prefetch_images
                ).annotate(total_like=Count('like_shoppers')).get(id=self.__product.id)

        self._test_model_instance_serialization(product, expected_data, context={'detail': True})

    def test_model_instance_serialization_list(self):
        expected_data = [
            self.__get_expected_data(self.__product)
        ]
        for data in expected_data:
            data['main_image'] = data['images'][0]['image_url']
        prefetch_images = Prefetch('images', to_attr='related_images')
        product = Product.objects.prefetch_related(
                    prefetch_images
                ).filter(id__in=[self.__product.id]).annotate(total_like=Count('like_shoppers'))
        serializer = self._get_serializer(product, many=True, context={'detail': False})
        
        for data in serializer.data:
            data.pop('shopper_like')

        self.assertListEqual(serializer.data, expected_data)

    def test_default_image_detail(self):
        product = ProductFactory()
        prefetch_images = Prefetch('images', to_attr='related_images')
        product = Product.objects.prefetch_related(prefetch_images).get(id=product.id)
        serializer = self._get_serializer(
            product, allow_fields=('id', 'images'), context={'detail': True}
        )
        expected_data = {
            'id': product.id,
            'images': [DEFAULT_IMAGE_URL],
        }

        self.assertDictEqual(
            {'id': serializer.data['id'], 'images': serializer.data['images']},
            expected_data
        )

    def test_default_image_list(self):
        ProductFactory()
        prefetch_images = Prefetch('images', to_attr='related_images')
        products = Product.objects.prefetch_related(prefetch_images).all()
        serializer = self._get_serializer(
            products, allow_fields=('id',), many=True, context={'detail': False}
        )
        expected_data = [
            {
                'id': product.id,
                'main_image': DEFAULT_IMAGE_URL if not product.images.all().exists() else get_full_image_url(product.images.all()[0].image_url),
            }
            for product in products
        ]

        self.assertListEqual(
            [{'id': data['id'], 'main_image': data['main_image']} for data in serializer.data],
            expected_data
        )

    def test_model_instance_serialization_like_true(self):
        shopper = ShopperFactory()
        shopper.like_products.add(self.__product)

        prefetch_images = Prefetch('images', to_attr='related_images')
        product = Product.objects.prefetch_related(prefetch_images).get(id=self.__product.id)
        serializer = self._get_serializer(
            product, context={'detail': True, 'shopper_like': ProductLike.objects.filter(shopper=shopper, product=product).exists()}
        )
        
        self.assertEqual(serializer.data['shopper_like'], True)

    def test_model_instance_serialization_list_like_true(self):
        prefetch_images = Prefetch('images', to_attr='related_images')
        products = Product.objects.prefetch_related(
                    prefetch_images
                ).filter(id__in=[self.__product.id])
        shopper = ShopperFactory()
        shopper.like_products.add(*products)

        shoppers_like_products_id_list = list(shopper.like_products.all().values_list('id', flat=True))
        serializer = self._get_serializer(
            products, many=True, context={'detail': False, 'shoppers_like_products_id_list': shoppers_like_products_id_list})
        expected_data = [shopper.like_products.filter(id=product.id).exists() for product in products]

        self.assertListEqual(
            [data['shopper_like'] for data in serializer.data],
            expected_data
        )

    def test_model_instance_serialization_list_like_false(self):
        prefetch_images = Prefetch('images', to_attr='related_images')
        products = Product.objects.prefetch_related(
                    prefetch_images
                ).filter(id__in=[self.__product.id])
        serializer = self._get_serializer(products, many=True, context={'detail': False})
        expected_data = [False for _ in products]
        
        self.assertListEqual(
            [data['shopper_like'] for data in serializer.data],
            expected_data
        )


class ProductWriteSerializerTestCase(SerializerTestCase):
    __batch_size = 2
    fixtures = ['temporary_image']
    _serializer_class = ProductWriteSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__image_url_list = list(TemporaryImage.objects.all().values_list('image_url', flat=True))
        cls.__sub_category_for_main_category_validation = SubCategoryFactory(
            main_category__product_additional_information_required=False,
            main_category__laundry_informations_required=False,
        )
        cls.__product = ProductFactory(additional_information=create_product_additional_information(True))
        ProductMaterialFactory.create_batch(size=cls.__batch_size, product=cls.__product, mixing_rate=50)

        cls.__product_colors = [
            ProductColorFactory(product=cls.__product, image_url=cls.__image_url_list.pop())
            for _ in range(cls.__batch_size)
        ]

        size_group = SettingGroupFactory(main_key='sizes')
        for product_color in cls.__product_colors:
            OptionFactory.create_batch(size=cls.__batch_size, product_color=product_color, size__group=size_group)

        for i in range(cls.__batch_size):
            ProductImageFactory(product=cls.__product, image_url=cls.__image_url_list.pop(), sequence=i+1)

        cls.__product.laundry_informations.add(*SettingItemFactory.create_batch(size=cls.__batch_size, group=SettingGroupFactory(main_key='laundry_information')))
        cls.__product.tags.add(*TagFactory.create_batch(size=cls.__batch_size))

        color_id_list = [color.id for color in ColorFactory.create_batch(size=2)]
        cls._test_data = {
            'name': 'name',
            'price': 50000,
            'base_discount_rate': 10,
            'sub_category': cls.__product.sub_category_id,
            'style': cls.__product.style_id,
            'target_age_group': cls.__product.target_age_group_id,
            'tags': [tag.id for tag in TagFactory.create_batch(size=cls.__batch_size)],
            'materials': [
                {
                    'material': '가죽',
                    'mixing_rate': 80,
                },
                {
                    'material': '면', 
                    'mixing_rate': 20,
                },
            ],
            'laundry_informations' : [laundry_information.id for laundry_information in cls.__product.laundry_informations.all()],
            'additional_information': {
                'thickness': cls.__product.additional_information.thickness_id,
                'see_through': cls.__product.additional_information.see_through_id,
                'flexibility': cls.__product.additional_information.flexibility_id,
                'lining': cls.__product.additional_information.lining_id,
            },
            'manufacturing_country': cls.__product.manufacturing_country,
            'images': [
                {
                    'image_url': get_full_image_url(cls.__image_url_list.pop()),
                    'sequence': 1
                },
                {
                    'image_url': get_full_image_url(cls.__image_url_list.pop()),
                    'sequence': 2
                },
                {
                    'image_url': get_full_image_url(cls.__image_url_list.pop()),
                    'sequence': 3
                }
            ],
            'colors': [
                {
                    'color': color_id_list[0],
                    'display_color_name': '다크',
                    'options': [{'size': data} for data in cls.__product_colors[0].options.values_list('size_id', flat=True)],
                    'image_url': get_full_image_url(cls.__image_url_list.pop()),
                },
                {
                    'color': color_id_list[1],
                    'display_color_name': '블랙',
                    'options': [{'size': data} for data in cls.__product_colors[1].options.values_list('size_id', flat=True)],
                    'image_url': get_full_image_url(cls.__image_url_list.pop()),
                }
            ]
        }

    def __set_up_main_category_validation_data(self, default=True, validation_for_update=False):
        if default:
            self._test_data = {
                'sub_category': self.__product.sub_category,
                'additional_information': True,
                'laundry_informations': True,
            }
        else:
            self._test_data = {
                'sub_category': self.__sub_category_for_main_category_validation,
            }

        if validation_for_update:
            self.__product.sub_category = self.__sub_category_for_main_category_validation

    def __assert_validate_main_category(self, expected_message, validation_for_update=False):
        self._test_serializer_raise_validation_error(
            expected_message, self._test_data,
            function=self._get_serializer(self.__product if validation_for_update else None)._ProductWriteSerializer__validate_main_category,
        )

    def test_validation_price(self):
        self._test_data['price'] = 50010
        expected_message = 'The price must be a multiple of 100.'

        self._test_serializer_raise_validation_error(expected_message)

    def test_raise_validation_error_color_length_more_than_limit(self):
        product_colors = [
            ProductColorFactory(product=self.__product, image_url=self.__image_url_list.pop())
            for _ in range(PRODUCT_COLOR_MAX_LENGTH + 1)
        ]
        for product_color in product_colors:
            OptionFactory(product_color=product_color)
        data = [
            {
                'display_color_name': product_color.display_color_name,
                'color': product_color.color.id,
                'options': [
                    {'size': option.size_id}
                    for option in product_color.options.all()
                ],
                'image_url': get_full_image_url(product_color.image_url),
            }for product_color in product_colors
        ]
        data += [
            {
                'id': product_color.id
            }for product_color in self.__product_colors
        ]
        expected_message = 'The product cannot have more than ten colors.'

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product, data={'colors': data}, partial=True
        )

    def test_raise_validation_error_delete_all_colors(self):
        data = [{'id': product_color.id} for product_color in self.__product.colors.all()]
        expected_message = 'The product must have at least one color.'

        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product, data={'colors': data}, partial=True
        )

    def test_raise_validation_error_pass_non_unique_display_color_name(self):
        data = [
            {
                'id': self.__product_colors[0].id,
                'display_color_name': self.__product_colors[1].display_color_name
            }
        ]
        expected_message = 'The product with the display_color_name already exists.'
        
        self._test_serializer_raise_validation_error(
            expected_message, instance=self.__product, data={'colors': data}, partial=True
        )

    def test_validate_no_additional_information(self):
        self.__set_up_main_category_validation_data()
        del self._test_data['additional_information']

        self.__assert_validate_main_category('This category requires additional_information.')

    def test_validate_no_additional_information_with_instance(self):
        self.__set_up_main_category_validation_data(validation_for_update=True)
        del self._test_data['additional_information']

        self.__assert_validate_main_category('This category requires additional_information.', True)

    def test_validate_additional_information(self):
        self.__set_up_main_category_validation_data(False)
        self._test_data['additional_information'] = True
        
        self.__assert_validate_main_category('This category cannot contain additional_information.')

    def test_validate_no_laundry_informations(self):
        self.__set_up_main_category_validation_data()
        del self._test_data['laundry_informations']

        self.__assert_validate_main_category('This category requires laundry_informations')

    def test_validate_no_laundry_informations_with_instance(self):
        self.__set_up_main_category_validation_data(validation_for_update=True)
        del self._test_data['laundry_informations']

        self.__assert_validate_main_category('This category requires laundry_informations.', True)

    def test_validate_laundry_informations(self):
        self.__set_up_main_category_validation_data(False)
        self._test_data['laundry_informations'] = True

        self.__assert_validate_main_category('This category cannot contain laundry_informations')

    def test_make_price_data(self):
        price = 50000
        base_discount_rate = 20
        self._test_data['price'] = price
        self._test_data['base_discount_rate'] = base_discount_rate
        
        serializer = self._get_serializer_after_validation(context={'wholesaler': WholesalerFactory()})
        product = serializer.save()

        expected_sale_price = 50000 * 2
        expected_base_discounted_price = expected_sale_price - (expected_sale_price * base_discount_rate/100) // 100 * 100

        self.assertEqual(expected_sale_price, product.sale_price)
        self.assertEqual(expected_base_discounted_price, product.base_discounted_price)

    def test_validated_data_for_update(self):
        self._test_data = {'sub_category': self.__sub_category_for_main_category_validation.id}

        self._test_validated_data({
            **self._test_data,
            'sub_category': self.__sub_category_for_main_category_validation,
            'additional_information': None,
            'laundry_informations': [],
        }, self.__product, partial=True)

    def test_create(self):
        serializer = self._get_serializer_after_validation(
            context={'wholesaler': WholesalerFactory()}
        )
        product = serializer.save()

        self.assertTrue(Product.objects.filter(id=product.id).exists())
        self.assertEqual(product.name, self._test_data['name'])
        self.assertEqual(product.price, self._test_data['price'])
        self.assertEqual(product.sub_category_id, self._test_data['sub_category'])
        self.assertEqual(product.style_id, self._test_data['style'])
        self.assertEqual(product.target_age_group_id, self._test_data['target_age_group'])
        self.assertEqual(product.additional_information, self.__product.additional_information)
        self.assertEqual(product.manufacturing_country, self._test_data['manufacturing_country'])
        self.assertListEqual(
            list(product.tags.all().order_by('id').values_list('id', flat=True)), 
            self._test_data['tags'],
        )
        self.assertListEqual(
            list(product.laundry_informations.all().order_by('id').values_list('id', flat=True)), 
            self._test_data['laundry_informations'],
        )
        self.assertEqual(product.images.all().count(), len(self._test_data['images']))
        self.assertEqual(product.materials.all().count(), len(self._test_data['materials']))
        self.assertEqual(product.colors.all().count(), len(self._test_data['colors']))
        self.assertEqual(
            Option.objects.filter(product_color__product=product).count(), 
            sum([len(color_data['options']) for color_data in self._test_data['colors']]),
        )

    def test_update_product_attribute(self):
        update_data = {
            'name': self.__product.name + '_update',
            'price': self.__product.price - 100,
            'sub_category': self.__sub_category_for_main_category_validation.id,
            'style': SettingItemFactory(group=self.__product.style.group).id,
            'target_age_group': SettingItemFactory(group=self.__product.target_age_group.group).id,
            'manufacturing_country': self.__product.manufacturing_country + '_update',
        }
        serializer = self._get_serializer_after_validation(
            self.__product, data=update_data, partial=True
        )
        product = serializer.save()

        self.assertTrue(Product.objects.filter(id=product.id).exists())
        self.assertEqual(product.name, update_data['name'])
        self.assertEqual(product.price, update_data['price'])
        self.assertEqual(product.sub_category_id, update_data['sub_category'])
        self.assertEqual(product.style_id, update_data['style'])
        self.assertEqual(product.target_age_group_id, update_data['target_age_group'])
        self.assertIsNone(product.additional_information)
        self.assertEqual(product.laundry_informations.count(), 0)
        self.assertEqual(product.manufacturing_country, update_data['manufacturing_country'])

    def test_update_id_only_m2m_fields(self):
        tags = TagFactory.create_batch(size=2)
        remaining_tags = random.sample(
            list(self.__product.tags.all().values_list('id', flat=True)), 
            2
        )
        tag_id_list = [tag.id for tag in tags] + remaining_tags
        tag_id_list.sort()

        update_data = {'tags': tag_id_list}
        serializer = self._get_serializer_after_validation(
            self.__product, data=update_data, partial=True
        )
        product = serializer.save()

        self.assertListEqual(
            list(product.tags.all().order_by('id').values_list('id', flat=True)),
            tag_id_list
        )

    def test_update_many_to_one_fields(self):
        materials = self.__product.materials.all()
        delete_materials = materials[:1]
        update_materials = materials[1:]
        create_data = [
            {
                'material': 'matcreate',
            }
        ]
        delete_data = list(delete_materials.values('id'))
        update_data = [
            {
                'id': material.id,
                'material': material.material + 'update',
                'mixing_rate': material.mixing_rate,
            }
            for material in update_materials
        ]
        for data in create_data:
            data['mixing_rate'] = 100 // len(create_data + update_data)
        for data in update_data:
            data['mixing_rate'] = 100 // len(create_data + update_data)

        data = {
            'materials': create_data + update_data + delete_data,
        }
        
        serializer = self._get_serializer_after_validation(
            self.__product, data=data, partial=True
        )
        product = serializer.save()

        deleted_id_list = [data['id'] for data in delete_data]
        updated_id_list = [data['id'] for data in update_data]

        self.assertTrue(not ProductMaterial.objects.filter(id__in=deleted_id_list).exists())
        self.assertListEqual(
            list(ProductMaterial.objects.filter(product=product).exclude(id__in=updated_id_list).values('material', 'mixing_rate')),
            create_data
        )
        self.assertListEqual(
            list(ProductMaterial.objects.filter(id__in=updated_id_list).values('id', 'material', 'mixing_rate')),
            update_data
        )

    def test_delete_product_colors_in_update(self):
        delete_product_color_id = self.__product.colors.latest('id').id
        data = {
            'colors': [
                {'id': delete_product_color_id}
            ]
        }
        serializer = self._get_serializer_after_validation(
            self.__product, data=data, partial=True
        )
        serializer.save()
        self.assertTrue(not ProductColor.objects.get(id=delete_product_color_id).on_sale)
        self.assertTrue(
            not Option.objects.filter(product_color_id=delete_product_color_id, on_sale=True).exists()
        )

    def test_create_product_colors_in_update(self):
        existing_color_id_list = list(self.__product.colors.all().values_list('id', flat=True))
        create_color_data = self._test_data['colors']
        create_option_data = [option_data for color_data in create_color_data for option_data in color_data['options']]
        data = {'colors': create_color_data}
        serializer = self._get_serializer_after_validation(self.__product, data=data, partial=True)
        serializer.save()

        self.assertListEqual(
            list(
                ProductColor.objects.filter(product=self.__product).exclude(id__in=existing_color_id_list)
                .order_by('id').values('color', 'display_color_name', 'image_url')
            ),
            [
                {
                    'color': d['color'],
                    'display_color_name': d['display_color_name']
                        if d['display_color_name'] is not None
                        else Color.objects.get(id=d['color']).name,
                    'image_url': d['image_url'].split(BASE_IMAGE_URL)[-1],
                }for d in data['colors']
            ]
        )
        self.assertListEqual(
            list(
                Option.objects.filter(product_color__product=self.__product)
                .exclude(product_color_id__in=existing_color_id_list).order_by('id')
                .values('size')
            ),
            [
                {'size': data['size']}
                for data in create_option_data
            ]
        )

    def test_update_product_colors_except_options(self):
        update_color_obj = self.__product.colors.latest('id')
        update_image_url = TemporaryImage.objects.first().image_url
        update_data = {
            'id': update_color_obj.id,
            'display_color_name': '_updated',
            'image_url': get_full_image_url(update_image_url)
        }
        data = {'colors': [update_data]}
        serializer = self._get_serializer_after_validation(
            self.__product, data=data, partial=True
        )
        serializer.save()

        updated_color_obj = self.__product.colors.get(id=update_color_obj.id)
        expected_dict = update_data
        expected_dict['image_url'] = update_image_url

        self.assertDictEqual(
            model_to_dict(updated_color_obj, fields=('id', 'display_color_name', 'image_url')),
            expected_dict
        )

    def test_create_option_in_update(self):
        update_color_obj = self.__product.colors.latest('id')
        existing_option_id_list = list(update_color_obj.options.values_list('id', flat=True))
        update_data = {
            'id': update_color_obj.id,
            'options': [{'size': SettingItemFactory(group=SettingGroup.objects.filter(main_key='sizes').first()).id}]
        }
        data = {'colors': [update_data]}
        serializer = self._get_serializer_after_validation(
            self.__product, data=data, partial=True
        )
        serializer.save()

        self.assertListEqual(
            list(
                Option.objects.filter(product_color=update_color_obj).exclude(id__in=existing_option_id_list)
                .order_by('id').values('size')
            ),
            update_data['options']
        )

    def test_update_price(self):
        update_data = {'price': 60000}
        serializer = self._get_serializer_after_validation(
            self.__product, data=update_data, partial=True
        )
        product = serializer.save()
        expected_sale_price = update_data['price'] * 2
        expected_base_discounted_price = expected_sale_price - (expected_sale_price * product.base_discount_rate / 100) // 100 * 100

        self.assertEqual(product.price, update_data['price'])
        self.assertEqual(product.sale_price, expected_sale_price)
        self.assertEqual(product.base_discounted_price, expected_base_discounted_price)

    def test_update_base_discount_rate(self):
        update_data = {'base_discount_rate': 20}
        serializer = self._get_serializer_after_validation(
            self.__product, data=update_data, partial=True
        )
        product = serializer.save()
        expected_base_discounted_price = product.sale_price - (product.sale_price * product.base_discount_rate / 100) // 100 * 100

        self.assertEqual(product.base_discounted_price, expected_base_discounted_price)

    def test_update_price_and_base_discount_rate(self):
        update_data = {'price': 60000, 'base_discount_rate': 20}
        serializer = self._get_serializer_after_validation(
            self.__product, data=update_data, partial=True
        )
        product = serializer.save()
        expected_sale_price = update_data['price'] * 2
        expected_base_discounted_price = expected_sale_price - (expected_sale_price * product.base_discount_rate / 100) // 100 * 100

        self.assertEqual(product.price, update_data['price'])
        self.assertEqual(product.sale_price, expected_sale_price)
        self.assertEqual(product.base_discounted_price, expected_base_discounted_price)

    def test_delete_option(self):
        update_color_obj = self.__product.colors.latest('id')
        delete_option_id = update_color_obj.options.latest('id').id
        update_data = {
            'id': update_color_obj.id,
            'options': [
                {
                    'id': delete_option_id
                }
            ]
        }
        data = {'colors': [update_data]}
        serializer = self._get_serializer_after_validation(
            self.__product, data=data, partial=True
        )
        serializer.save()

        self.assertTrue(not Option.objects.get(id=delete_option_id).on_sale)


class ProductQuestionAnswerClassificationSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductQuestionAnswerClassificationSerializer

    def test_model_instance_serialization(self):
        classification = ProductQuestionAnswerClassificationFactory()
        expected_data = {
            'id': classification.id,
            'name': classification.name,
        }

        self._test_model_instance_serialization(classification, expected_data)


class ProductQuestionAnswerSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductQuestionAnswerSerializer

    @classmethod
    def setUpTestData(cls):
        cls.__question_answer = ProductQuestionAnswerFactory()

    def test_model_instance_serialization(self):
        expected_data = {
            'id': self.__question_answer.id,
            'shopper': self.__question_answer.shopper.id,
            'created_at': datetime_to_iso(self.__question_answer.created_at),
            'username': self.__question_answer.shopper.username[:3] + '***',
            'classification': self.__question_answer.classification.name,
            'question': self.__question_answer.question,
            'answer': self.__question_answer.answer,
            'is_secret': self.__question_answer.is_secret,
        }

        self._test_model_instance_serialization(self.__question_answer, expected_data)

    def test_create(self):
        product = ProductFactory()
        shopper = ShopperFactory()
        data = {
            'question': 'question',
            'is_secret': True,
            'classification': ProductQuestionAnswerClassificationFactory().id,
        }
        serializer = self._get_serializer_after_validation(data=data)
        question_answer = serializer.save(product=product, shopper=shopper)

        self.assertTrue(ProductQuestionAnswer.objects.filter(id=question_answer.id).exists())
        self.assertEqual(question_answer.product, product)
        self.assertEqual(question_answer.shopper, shopper)
        self.assertEqual(question_answer.classification.id, data['classification'])
        self.assertEqual(question_answer.question, data['question'])
        self.assertEqual(question_answer.is_secret, data['is_secret'])

    def test_update(self):
        data = {
            'question': self.__question_answer.question + '_update',
            'is_secret': not self.__question_answer.is_secret,
            'classification':ProductQuestionAnswerClassificationFactory().id
        }

        serializer = self._get_serializer_after_validation(self.__question_answer, data=data)
        question_answer = serializer.save()

        self.assertTrue(ProductQuestionAnswer.objects.filter(id=question_answer.id).exists())
        self.assertEqual(question_answer.question, data['question'])
        self.assertEqual(question_answer.is_secret, data['is_secret'])
        self.assertEqual(question_answer.classification.id, data['classification'])


class ProductRegistrationSerializerTestCase(SerializerTestCase):
    _serializer_class = ProductRegistrationSerializer

    def test_model_instance_serialization(self):
        instances = get_product_registration_test_data()

        self._test_model_instance_serialization(instances, {
            'main_categories': MainCategorySerializer(instances['main_categories'], exclude_fields=['id', 'image_url'], many=True).data,
            'colors': ColorSerializer(instances['colors'], many=True).data,
            **SettingGroupSerializer(instances['setting_groups'], many=True).data
        })
        