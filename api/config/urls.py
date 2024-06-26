from django.conf.urls import handler403, handler404, handler500, handler400
from django.urls import path, include, re_path

from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from drf_yasg.views import get_schema_view
from drf_yasg.openapi import Info, License

from product.documentations import DecoratedProductViewSet
from order.documentations import DecoratedOrderViewSet
from coupon.documentations import DecoratedCouponViewSet


handler404 = 'common.views.custom_404_view'
handler500 = 'common.views.custom_500_view'

schema_view = get_schema_view(
   Info(
      # todo 서비스 약관(terms_of_service), 컨텍센터(contact)
      title="Omios API", # API 제목
      default_version='v1', # API 버전, Swagger 버전과 다름
      description="Omios REST API 문서", # API 설명, markdown 지원
      license=License(name="BSD License"), # license 오브젝트
   ),
   # url="http://13.209.244.41",
   public=True,
   permission_classes=(AllowAny,),
)

router = SimpleRouter(trailing_slash=False)
router.register(r'products', DecoratedProductViewSet, basename='products')
router.register(r'^orders', DecoratedOrderViewSet, basename='orders')
router.register(r'^coupons', DecoratedCouponViewSet, basename='coupons')

urlpatterns = [
   re_path(r'^swagger$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('users', include('user.urls')),
   path('products', include('product.urls')),
   path('orders', include('order.urls')),
   path('coupons', include('coupon.urls')),
]

urlpatterns += router.urls
