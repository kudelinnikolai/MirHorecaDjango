from django.urls import path, include
from .views import *

# shop_urls = [
#   path('collection_<slug:collection>', collection, name='collection'),
#   path('<slug:category>', category, name='category'), 
#   path('<slug:category>/<slug:base_product>', base_product, name='base_product'),
#   path('<slug:category>/<slug:base_product>/<slug:product_variant>', product_variant, name='product_variant'),
# ]

# urlpatterns = [
#   path('', index, name='home'),
#   path('about', about, name='about'),
#   path('contact', contact, name='contact'),
#   path('privacy-policy', privacy, name='privacy'),
#   path('delivery', delivery, name='delivery'),
#   path('payment', payment, name='payment'),

#   path('shop', include(shop_urls)),
# ]


urlpatterns = [
  path('', base_categories, name='home'),
  path('about', about, name='about'),
  path('contact', contact, name='contact'),
  path('privacy-policy', privacy, name='privacy'),
  path('delivery', delivery, name='delivery'),
  path('payment', payment, name='payment'),
  path('robots.txt', robots, name='robots'),
  path('categories', base_categories, name='base_categories'),
  path('collections', main_collections, name='main_collections'),
  
  path('collections/<slug:collection>', collection, name='collection'),
  path('<slug:category>', category, name='category'),
  path('<slug:category>/<slug:base_product>_<slug:color_of_base_product>_<slug:product_variant>', product_variant, name='product_variant'),
  path('<slug:category>/<slug:base_product>_<slug:color_of_base_product>', color_of_base_product, name='color_of_base_product'),
  path('<slug:category>/<slug:base_product>', base_product, name='base_product'),
]