from typing import Any
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from .helpers.imageSaver import set_12_images_from_1, delete_all_images_with_this_name, get_small_image_url
import os

# Create your models here.


# _______________________________________________________________
# _________________Валидаторы__________________________________
# _______________________________________________________________

def validate_slug_without_underlines(value):
    if "_" in value:
        raise ValidationError("Нельзя использовать знак нижнего подчеркивания в URL-идентификаторе базового товара или варианта товара!")
    else:
        return value

# _______________________________________________________________
# _________________Пользователи__________________________________
# _______________________________________________________________



class CustomUser(AbstractUser):
  """Кастомная модель пользователя сайта"""
  favorite_products = models.ManyToManyField('ProductVariant', through='UserFavorite', through_fields=('user', 'product_variant'), verbose_name ='Избранное', related_name='voters')
  reviews = models.ManyToManyField('ProductVariant', through='UserReview', through_fields=('user', 'product_variant'), verbose_name ='Отзывы на товары', related_name='raters')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Пользователи'
    verbose_name ='Пользователь'

  def __str__(self):
    return self.username




class UserFavorite(models.Model):
  """Избранное. Реализует через себя связь manyToMany между товарами и пользователями"""
  user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name ='Пользователь', on_delete=models.CASCADE)
  product_variant = models.ForeignKey('ProductVariant', verbose_name ='Товар', on_delete=models.CASCADE)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Избранное'
    verbose_name ='Избранное'

  def __str__(self):
    return '%s понравилась %s' % (self.user, self.product_variant)
  



class UserReview(models.Model):
  """Отзывы пользователя на товар. Реализует через себя связь manyToMany между товарами и пользователями"""
  user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name ='Пользователь', on_delete=models.CASCADE)
  product_variant = models.ForeignKey('ProductVariant', verbose_name ='Товар', on_delete=models.CASCADE)
  rating = models.PositiveSmallIntegerField('Оценка', default=0, blank=False)
  text = models.TextField('Комментарий', blank=True, default='')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Отзывы'
    verbose_name ='Отзыв'

  def __str__(self):
    return '%s лайкнул %s' % (self.user, self.product_variant)



class Adress(models.Model):
  """Справочник для пользователей"""
  user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
  )
  country = models.CharField('Страна', max_length=70,  default="Россия", blank=False)
  region = models.CharField('Регион', max_length=70,  blank=True, default='')
  city = models.CharField('Город', max_length=70)
  street = models.CharField('Улица', max_length=70)
  house = models.CharField('Дом', max_length=70) 
  flat = models.CharField('Квартира', max_length=70)
  zip_code = models.CharField('Индекс', max_length=70, blank=True, default='')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Адреса'
    verbose_name ='Адрес'

  def __str__(self):
    return '%s, %s, %s, %s %s, кв %s.' % (self.country, self.region, self.city, self.street, self.house, self.flat)



class Order(models.Model):
  """Заказы. """
  STATUS = [
      ('0', 'In cart'),
      ('1', 'New'),
      ('2', 'Processing'),
      ('3', 'Paid'),
      ('4', 'Ready to shipping'),
      ('5', 'Shipped'),
  ]
  status = models.CharField(max_length=2, choices=STATUS, blank=False, default='1')
  comment = models.TextField('Комментарий', blank=True, default='')
  adress = models.ForeignKey('Adress', verbose_name ='Адрес', on_delete=models.CASCADE)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name ='Пользователь', on_delete=models.SET_NULL, null=True, blank=True)

  products = models.ManyToManyField('ProductVariant', through="ProductsInOrder", through_fields=('order', 'product_variant'), verbose_name ='Товары в заказе')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Заказы'
    verbose_name ='Заказ'

  def __str__(self):
    return 'заказ %s от пользователя %s' % (self.pk, self.user)




class ProductsInOrder(models.Model):
  """Товары в заказе. Реализует через себя связь manyToMany между товарами и заказами"""
  amount = models.PositiveSmallIntegerField('Количество', default=1, blank=False)
  order = models.ForeignKey('Order', verbose_name ='Заказ', on_delete=models.CASCADE)
  product_variant = models.ForeignKey('ProductVariant', verbose_name ='Товар', on_delete=models.CASCADE)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Товары в заказе'
    verbose_name ='Товар в заказе'



# _______________________________________________________________
# _________________Товары________________________________________
# _______________________________________________________________

class BaseProduct(models.Model):
  """Базовый продукт, который может иметь несколько вариантов"""
  name = models.CharField('Название товара', max_length=70, unique=True)
  description = models.TextField('Описание', blank=True, default='')
  slug = models.SlugField('URL-идентификатор', max_length=60, unique=True, validators=[validate_slug_without_underlines],)
  colors = models.ManyToManyField('Color', through="ColorsOfBaseProduct", through_fields=('base_product','color' ), verbose_name ='Цвета базового товара', related_name="products")
  category = models.ForeignKey('Category', verbose_name ='Категория', on_delete=models.PROTECT, related_name="products")
  collection = models.ForeignKey('Collection', verbose_name ='Коллекция', on_delete=models.PROTECT, blank=True, null=True, related_name="products")
  country = models.ForeignKey('Country', verbose_name ='Страна', on_delete=models.SET_NULL, blank=True, null=True)
  material = models.ForeignKey('Material', verbose_name ='Материал', on_delete=models.SET_NULL, blank=True, null=True)
  geometry_form = models.ForeignKey('GeometryForm', verbose_name ='Форма', on_delete=models.SET_NULL, blank=True, null=True)
  nonstick_type= models.ForeignKey('NonstickType', verbose_name ='Тип антипригарного покрытия', on_delete=models.SET_NULL, blank=True, null=True)

  wall_thickness = models.DecimalField('Толщина стенок (см)', max_digits=10, decimal_places=1, null=True, blank=True)
  is_for_microvawe = models.BooleanField('Подходит для микроволновки?', null=True, blank=True)

  is_for_gas_stoves = models.BooleanField('Подходит для газовой плиты?', null=True, blank=True)
  is_for_electric_stoves = models.BooleanField('Подходит для электроплиты?', null=True, blank=True)
  is_for_glass_ceramic_stoves = models.BooleanField('Подходит для стеклокерамической плиты?', null=True, blank=True)
  is_for_induction_stoves = models.BooleanField('Подходит для индукционной плиты?', null=True, blank=True)
  is_for_oven = models.BooleanField('Подходит для духовки?', null=True, blank=True)
  is_for_halogen_burners = models.BooleanField('Подходит для галогеновой конфорки?', null=True, blank=True)
  is_for_open_fire = models.BooleanField('Подходит для открытого огня?', null=True, blank=True)
  is_for_dishwasher = models.BooleanField('Подходит для посудомойки?', null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    # ordering = ["created_at"]
    verbose_name_plural = 'Базовые товары'
    verbose_name ='Базовый товар'
    # constraints = [] --- хорошо бы добавить ограничение, что slug-и базовых товаров и slug-и вариантов должны быть совместно-уникальны 
    # indexes = []

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('base_product', kwargs={'base_product' : self.slug, 'category' : self.category.slug})




class ColorsOfBaseProduct(models.Model):
  """Цвета базовых товаров. Реализует через себя ManyToMany между Базовыми товарами и Цветами"""
  base_product = models.ForeignKey('BaseProduct', verbose_name ='Базовый товар', on_delete=models.CASCADE, related_name="colorsOfVariants")
  color = models.ForeignKey('Color', verbose_name ='Цвет', on_delete=models.CASCADE)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Цвета базовых товаров'
    verbose_name ='Цвет базового товара'

  def __str__(self):
    return '%s | %s ' % (self.base_product, self.color)
  
  def get_absolute_url(self):
    return reverse('color_of_base_product', kwargs={'category' : self.base_product.category.slug, 'base_product' : self.base_product.slug, 'color_of_base_product' : self.color.slug})





class ProductVariant(models.Model):
  """Различные варианты отдельных базовых товаров. Если варианты различаются какими-то иными параметрами, нежели указанными здесь, то это разные товары, а не варианты"""
  color_of_base_product = models.ForeignKey('ColorsOfBaseProduct', verbose_name ='Базовый товар и его цвет', on_delete=models.CASCADE, related_name="variants")
  
  featureName = models.CharField('Название варианта товара', max_length=70, ) # Если захотим сделать отдельные траницы для вариантов товаров
  slug = models.SlugField('URL-идентификатор варианта товара', max_length=70, validators=[validate_slug_without_underlines], ) # нужно уникализироать его от базового товара. Это можно сделать добавлением одной/нескольких характеристик, заполненной при добавлении Варианта
  articul = models.CharField('Артикул', max_length=30, unique=True)
  residue = models.PositiveSmallIntegerField('Остаток', default=1 , blank=False)
  extra_color = models.ForeignKey('Color', verbose_name ='Дополнительный цвет', on_delete=models.SET_NULL, blank=True,null=True)
  price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=2)
  diameter = models.DecimalField('Диаметр (см)', max_digits=10, decimal_places=1, null=True, blank=True) # Заполнять все размеры не надо! 
  depth = models.DecimalField('Глубина (см)', max_digits=10, decimal_places=1, null=True, blank=True)
  height = models.DecimalField('Высота (см)', max_digits=10, decimal_places=1, null=True, blank=True)
  width = models.DecimalField('Ширина (см)', max_digits=10, decimal_places=1, null=True, blank=True)
  length = models.DecimalField('Длина (см)', max_digits=10, decimal_places=1, null=True, blank=True)
  value = models.DecimalField('Объем (л)', max_digits=10, decimal_places=2, null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    # order_with_respect_to = 'base_product'
    verbose_name_plural = 'Варианты товара'
    verbose_name ='Вариант товара'

  def __str__(self):
    return '%s | %s | %s' % (self.color_of_base_product.base_product, self.color_of_base_product.color, self.slug)
  
  def get_absolute_url(self):
    return reverse('product_variant', kwargs={'category' : self.color_of_base_product.base_product.category.slug, 'base_product' : self.color_of_base_product.base_product.slug, 'color_of_base_product' : self.color_of_base_product.color.slug, 'product_variant' : self.slug})




def categoryImg_directory_path(instance, filename):
  return '{0}/{1}'.format(instance.slug, filename)

class Category(models.Model):
  """Категории тоавров. Поддерживает вложенность"""
  parent_category = models.ForeignKey('self', verbose_name ='Родительская категория', on_delete = models.PROTECT, blank=True, null=True)
  name = models.CharField('Название', max_length=150, unique=True)
  slug = models.SlugField('URL-идентификатор', max_length=60, unique=True, validators=[validate_slug_without_underlines],)
  image = models.ImageField('Изображение', upload_to=categoryImg_directory_path, max_length=255)
  order = models.PositiveIntegerField(default=0, blank=True, null=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def directory_path(self):
    return '{0}/'.format(self.slug)

  def get_html_image(self):
    if self.image.url is not None:
      return mark_safe(f'<a href="{self.url_image_1600_jpg()}"><img src="{self.url_image_70_jpg()}"  style="object-fit: contain;width:70px;aspect-ratio:1/1;"></a>') 
  get_html_image.short_description = 'Фото'
  
  class Meta:
    ordering = ['order',]
    get_latest_by = ['created_at']
    verbose_name_plural = 'Категории'
    verbose_name ='Категория'

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return reverse('category', kwargs={'category' : self.slug})
  
  def save(self, *args, **kwargs):
    is_old = bool(self.pk)
    if is_old:
      # Если изменяем запись, а не создаем новую - запоминаем прежнее состояние
      old_obj = Category.objects.get(pk=self.pk)

    super().save(*args, **kwargs)
    # узнаем путь до новой картинки
    new_img_path = os.path.normpath(self.image.__str__())
    new_img_fullpath = os.path.normpath(self.image.path)
    new_img_fullName = os.path.basename(new_img_path)
    new_standart_img_path = os.path.normpath('{0}/{1}'.format(self.slug, new_img_fullName)).replace(os.sep, '/')
    new_standart_img_fullpath = os.path.normpath(os.path.join(settings.MEDIA_ROOT, new_standart_img_path))

    if is_old:
      if (new_img_fullpath != new_standart_img_path) and (os.path.isfile(new_img_fullpath)):
      # Если путь нестандартный, то делаем его стандартным, а картинку выносим в нужную папку
        os.makedirs(os.path.dirname(new_standart_img_fullpath), exist_ok=True)
        os.rename(new_img_fullpath, new_standart_img_fullpath)
        self.image = new_standart_img_path
        super().save(*args, **kwargs)

    set_12_images_from_1(self)

    if is_old:
      if self.image.path != old_obj.image.path:
      # Если перезаписываем картинку - надо удалить все старые копии
        delete_all_images_with_this_name(old_obj)
  

  def delete(self, *args, **kwargs):
    delete_all_images_with_this_name(self)
    super().delete( *args, **kwargs)


  def url_image_1600_jpg(self):
    return get_small_image_url(self.image.url, '1600', 'jpg')
  def url_image_800_jpg(self):
    return get_small_image_url(self.image.url, '800', 'jpg')
  def url_image_400_jpg(self):
    return get_small_image_url(self.image.url, '400', 'jpg')
  def url_image_70_jpg(self):
    return get_small_image_url(self.image.url, '70', 'jpg')
  def url_image_1600_webp(self):
    return get_small_image_url(self.image.url, '1600', 'webp')
  def url_image_800_webp(self):
    return get_small_image_url(self.image.url, '800', 'webp')
  def url_image_400_webp(self):
    return get_small_image_url(self.image.url, '400', 'webp')
  def url_image_70_webp(self):
    return get_small_image_url(self.image.url, '70', 'webp')
  def url_image_1600_avif(self):
    return get_small_image_url(self.image.url, '1600', 'avif')
  def url_image_800_avif(self):
    return get_small_image_url(self.image.url, '800', 'avif')
  def url_image_400_avif(self):
    return get_small_image_url(self.image.url, '400', 'avif')
  def url_image_70_avif(self):
    return get_small_image_url(self.image.url, '70', 'avif')





def collectionImg_directory_path(instance, filename):
  return 'collections/{0}/{1}'.format(instance.slug, filename)

class Collection(models.Model):
  """Коллекции товаров. Простейший справочник"""
  name = models.CharField('Название', max_length=150, unique=True)
  description = models.TextField('Описание', blank=True, default='')
  slug = models.SlugField('URL-идентификатор', max_length=60, unique=True, validators=[validate_slug_without_underlines],)
  image = models.ImageField('Изображение', upload_to=collectionImg_directory_path, max_length=255)
  order = models.PositiveIntegerField(default=0, blank=True, null=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True) 

  def get_html_image(self):
    if self.image.url is not None:
      return mark_safe(f'<a href="{self.url_image_1600_jpg()}"><img src="{self.url_image_70_jpg()}"  style="object-fit: contain;width:70px;aspect-ratio:1/1;"></a>') 
  get_html_image.short_description = 'Фото'

  class Meta:
    ordering = ['order',]
    get_latest_by = ['created_at']
    verbose_name_plural = 'Коллекции'
    verbose_name ='Коллекция'

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('collection', kwargs={'collection' : self.slug})
  
  def save(self, *args, **kwargs):
    is_old = bool(self.pk)
    if is_old:
      # Если изменяем запись, а не создаем новую - запоминаем прежнее состояние
      old_obj = Collection.objects.get(pk=self.pk)

    super().save(*args, **kwargs)
    # узнаем путь до новой картинки
    new_img_path = os.path.normpath(self.image.__str__())
    new_img_fullpath = os.path.normpath(self.image.path)
    new_img_fullName = os.path.basename(new_img_path)
    new_standart_img_path = os.path.normpath('collections/{0}/{1}'.format(self.slug, new_img_fullName)).replace(os.sep, '/')
    new_standart_img_fullpath = os.path.normpath(os.path.join(settings.MEDIA_ROOT, new_standart_img_path))

    if is_old:
      if (new_img_fullpath != new_standart_img_path) and (os.path.isfile(new_img_fullpath)):
      # Если путь нестандартный, то делаем его стандартным, а картинку выносим в нужную папку
        os.makedirs(os.path.dirname(new_standart_img_fullpath), exist_ok=True)
        os.rename(new_img_fullpath, new_standart_img_fullpath)
        self.image = new_standart_img_path
        super().save(*args, **kwargs)

    set_12_images_from_1(self)

    if is_old:
      if self.image.path != old_obj.image.path:
      # Если перезаписываем картинку - надо удалить все старые копии
        delete_all_images_with_this_name(old_obj)
  
  def delete(self, *args, **kwargs):
    delete_all_images_with_this_name(self)
    super().delete( *args, **kwargs)


  def url_image_1600_jpg(self):
    return get_small_image_url(self.image.url, '1600', 'jpg')
  def url_image_800_jpg(self):
    return get_small_image_url(self.image.url, '800', 'jpg')
  def url_image_400_jpg(self):
    return get_small_image_url(self.image.url, '400', 'jpg')
  def url_image_70_jpg(self):
    return get_small_image_url(self.image.url, '70', 'jpg')
  def url_image_1600_webp(self):
    return get_small_image_url(self.image.url, '1600', 'webp')
  def url_image_800_webp(self):
    return get_small_image_url(self.image.url, '800', 'webp')
  def url_image_400_webp(self):
    return get_small_image_url(self.image.url, '400', 'webp')
  def url_image_70_webp(self):
    return get_small_image_url(self.image.url, '70', 'webp')
  def url_image_1600_avif(self):
    return get_small_image_url(self.image.url, '1600', 'avif')
  def url_image_800_avif(self):
    return get_small_image_url(self.image.url, '800', 'avif')
  def url_image_400_avif(self):
    return get_small_image_url(self.image.url, '400', 'avif')
  def url_image_70_avif(self):
    return get_small_image_url(self.image.url, '70', 'avif')




# _______________________________________________________________
# _________________СПРАВОЧНИКИ ДЛЯ ТОВАРОВ_______________________
# _______________________________________________________________
  
def baseProductImg_directory_path(instance, filename): 
  category = instance.base_product.category.slug
  product= instance.base_product.slug
  return '{0}/{1}/{2}'.format(category, product, filename)

class BaseProductImg(models.Model):
  """Картинки для базовых товаров"""
  
  base_product = models.ForeignKey(BaseProduct, verbose_name ='Базовый товар', on_delete = models.PROTECT)
  alt = models.CharField('alt-текст для SEO', max_length=150, default='', blank=True)
  image = models.ImageField('Изображение', upload_to=baseProductImg_directory_path, max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True) 

  def get_html_image(self):
    if self.image.url is not None:
      return mark_safe(f'<a href="{self.url_image_1600_jpg()}"><img src="{self.url_image_70_jpg()}"  style="object-fit: contain;width:70px;aspect-ratio:1/1;"></a>') 
  get_html_image.short_description = 'Фото'

  class Meta:
    get_latest_by = ['created_at']
    # order_with_respect_to = 'product_variant'
    verbose_name_plural = 'Изображения базовых товаров'
    verbose_name ='Изображение базового товара'

  def __str__(self):
    return 'изображение для %s' % (self.base_product, )
  
  def save(self, *args, **kwargs):
    is_old = bool(self.pk)
    if is_old:
      # Если изменяем запись, а не создаем новую - запоминаем прежнее состояние
      old_obj = BaseProductImg.objects.get(pk=self.pk)

    super().save(*args, **kwargs)
    # узнаем путь до новой картинки
    new_img_path = os.path.normpath(self.image.__str__())
    new_img_fullpath = os.path.normpath(self.image.path)
    new_img_fullName = os.path.basename(new_img_path)
    new_standart_img_path = os.path.normpath('{0}/{1}/{2}'.format(self.base_product.category.slug, self.base_product.slug, new_img_fullName)).replace(os.sep, '/')
    new_standart_img_fullpath = os.path.normpath(os.path.join(settings.MEDIA_ROOT, new_standart_img_path))

    if is_old:
      if (new_img_fullpath != new_standart_img_path) and (os.path.isfile(new_img_fullpath)):
      # Если путь нестандартный, то делаем его стандартным, а картинку выносим в нужную папку
        os.makedirs(os.path.dirname(new_standart_img_fullpath), exist_ok=True)
        os.rename(new_img_fullpath, new_standart_img_fullpath)
        self.image = new_standart_img_path
        super().save(*args, **kwargs)

    set_12_images_from_1(self)

    if is_old:
      if self.image.path != old_obj.image.path:
      # Если перезаписываем картинку - надо удалить все старые копии
        delete_all_images_with_this_name(old_obj)
  
  def delete(self, *args, **kwargs):
    delete_all_images_with_this_name(self)
    super().delete( *args, **kwargs)

  def url_image_1600_jpg(self):
    return get_small_image_url(self.image.url, '1600', 'jpg')
  def url_image_800_jpg(self):
    return get_small_image_url(self.image.url, '800', 'jpg')
  def url_image_400_jpg(self):
    return get_small_image_url(self.image.url, '400', 'jpg')
  def url_image_70_jpg(self):
    return get_small_image_url(self.image.url, '70', 'jpg')
  def url_image_1600_webp(self):
    return get_small_image_url(self.image.url, '1600', 'webp')
  def url_image_800_webp(self):
    return get_small_image_url(self.image.url, '800', 'webp')
  def url_image_400_webp(self):
    return get_small_image_url(self.image.url, '400', 'webp')
  def url_image_70_webp(self):
    return get_small_image_url(self.image.url, '70', 'webp')
  def url_image_1600_avif(self):
    return get_small_image_url(self.image.url, '1600', 'avif')
  def url_image_800_avif(self):
    return get_small_image_url(self.image.url, '800', 'avif')
  def url_image_400_avif(self):
    return get_small_image_url(self.image.url, '400', 'avif')
  def url_image_70_avif(self):
    return get_small_image_url(self.image.url, '70', 'avif')
  

  

def colorOfProductImg_directory_path(instance, filename):
  category = instance.color_of_base_product.base_product.category.slug
  product= instance.color_of_base_product.base_product.slug
  color= instance.color_of_base_product.color.slug
  return '{0}/{1}/{2}/{3}'.format(category, product, color, filename)

class ColorOfProductImg(models.Model):
  """Картинки для цветов базовых товаров товаров"""
  
  color_of_base_product = models.ForeignKey(ColorsOfBaseProduct, verbose_name ='Цвет базового товара', on_delete = models.PROTECT, related_name="images")
  alt = models.CharField('alt-текст для SEO', max_length=150, default='', blank=True)
  image = models.ImageField('Изображение', upload_to=colorOfProductImg_directory_path, max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True) 

  def get_html_image(self):
    if self.image.url is not None:
      return mark_safe(f'<a href="{self.url_image_1600_jpg()}"><img src="{self.url_image_70_jpg()}"  style="object-fit: contain;width:70px;aspect-ratio:1/1;"></a>') 
  get_html_image.short_description = 'Фото'

  class Meta:
    get_latest_by = ['created_at']
    # order_with_respect_to = 'product_variant'
    verbose_name_plural = 'Изображения цвета базового товара'
    verbose_name ='Изображение цвета базового товара'

  def __str__(self):
    return 'изображение для %s' % (self.color_of_base_product,)
  
  def save(self, *args, **kwargs):
    is_old = bool(self.pk)
    if is_old:
      # Если изменяем запись, а не создаем новую - запоминаем прежнее состояние
      old_obj = ColorOfProductImg.objects.get(pk=self.pk)

    super().save(*args, **kwargs)
    # узнаем путь до новой картинки
    new_img_path = os.path.normpath(self.image.__str__())
    new_img_fullpath = os.path.normpath(self.image.path)
    new_img_fullName = os.path.basename(new_img_path)
    new_standart_img_path = os.path.normpath('{0}/{1}/{2}/{3}'.format(self.color_of_base_product.base_product.category.slug, self.color_of_base_product.base_product.slug, self.color_of_base_product.color.slug, new_img_fullName)).replace(os.sep, '/')
    new_standart_img_fullpath = os.path.normpath(os.path.join(settings.MEDIA_ROOT, new_standart_img_path))

    if is_old:
      if (new_img_fullpath != new_standart_img_path) and (os.path.isfile(new_img_fullpath)):
      # Если путь нестандартный, то делаем его стандартным, а картинку выносим в нужную папку
        os.makedirs(os.path.dirname(new_standart_img_fullpath), exist_ok=True)
        os.rename(new_img_fullpath, new_standart_img_fullpath)
        self.image = new_standart_img_path
        super().save(*args, **kwargs)

    set_12_images_from_1(self)

    if is_old:
      if self.image.path != old_obj.image.path:
      # Если перезаписываем картинку - надо удалить все старые копии
        delete_all_images_with_this_name(old_obj)
  
  def delete(self, *args, **kwargs):
    delete_all_images_with_this_name(self)
    super().delete( *args, **kwargs)

  def url_image_1600_jpg(self):
    return get_small_image_url(self.image.url, '1600', 'jpg')
  def url_image_800_jpg(self):
    return get_small_image_url(self.image.url, '800', 'jpg')
  def url_image_400_jpg(self):
    return get_small_image_url(self.image.url, '400', 'jpg')
  def url_image_70_jpg(self):
    return get_small_image_url(self.image.url, '70', 'jpg')
  def url_image_1600_webp(self):
    return get_small_image_url(self.image.url, '1600', 'webp')
  def url_image_800_webp(self):
    return get_small_image_url(self.image.url, '800', 'webp')
  def url_image_400_webp(self):
    return get_small_image_url(self.image.url, '400', 'webp')
  def url_image_70_webp(self):
    return get_small_image_url(self.image.url, '70', 'webp')
  def url_image_1600_avif(self):
    return get_small_image_url(self.image.url, '1600', 'avif')
  def url_image_800_avif(self):
    return get_small_image_url(self.image.url, '800', 'avif')
  def url_image_400_avif(self):
    return get_small_image_url(self.image.url, '400', 'avif')
  def url_image_70_avif(self):
    return get_small_image_url(self.image.url, '70', 'avif')
  

  

def productVariantImg_directory_path(instance, filename):
  category = instance.product_variant.color_of_base_product.base_product.category.slug
  product= instance.product_variant.color_of_base_product.base_product.slug
  color= instance.product_variant.color_of_base_product.color.slug
  variant= instance.product_variant.slug
  return '{0}/{1}/{2}/{3}/{4}'.format(category, product, color, variant, filename)

class ProductVariantImg(models.Model):
  """Картинки для вариантов товаров"""
  
  product_variant = models.ForeignKey(ProductVariant, verbose_name ='Вариант товара', on_delete = models.PROTECT, related_name="images")
  alt = models.CharField('alt-текст для SEO', max_length=150, default='', blank=True)
  image = models.ImageField('Изображение', upload_to=productVariantImg_directory_path, max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True) 

  def get_html_image(self):
    if self.image.url is not None:
      return mark_safe(f'<a href="{self.url_image_1600_jpg()}"><img src="{self.url_image_70_jpg()}"  style="object-fit: contain;width:70px;aspect-ratio:1/1;"></a>') 
  get_html_image.short_description = 'Фото'

  class Meta:
    get_latest_by = ['created_at']
    # order_with_respect_to = 'product_variant'
    verbose_name_plural = 'Изображения вариантов товаров'
    verbose_name ='Изображение варианта товара'

  def __str__(self):
    return 'изображение для %s' % (self.product_variant,)
  
  def save(self, *args, **kwargs):
    is_old = bool(self.pk)
    if is_old:
      # Если изменяем запись, а не создаем новую - запоминаем прежнее состояние
      old_obj = ProductVariantImg.objects.get(pk=self.pk)

    super().save(*args, **kwargs)
    # узнаем путь до новой картинки
    new_img_path = os.path.normpath(self.image.__str__())
    new_img_fullpath = os.path.normpath(self.image.path)
    new_img_fullName = os.path.basename(new_img_path)
    new_standart_img_path = os.path.normpath('{0}/{1}/{2}/{3}/{4}'.format(self.product_variant.color_of_base_product.base_product.category.slug, self.product_variant.color_of_base_product.base_product.slug, self.product_variant.color_of_base_product.color.slug, self.product_variant.slug, new_img_fullName)).replace(os.sep, '/')
    new_standart_img_fullpath = os.path.normpath(os.path.join(settings.MEDIA_ROOT, new_standart_img_path))

    if is_old:
      if (new_img_fullpath != new_standart_img_path) and (os.path.isfile(new_img_fullpath)):
      # Если путь нестандартный, то делаем его стандартным, а картинку выносим в нужную папку
        os.makedirs(os.path.dirname(new_standart_img_fullpath), exist_ok=True)
        os.rename(new_img_fullpath, new_standart_img_fullpath)
        self.image = new_standart_img_path
        super().save(*args, **kwargs)

    set_12_images_from_1(self)

    if is_old:
      if self.image.path != old_obj.image.path:
      # Если перезаписываем картинку - надо удалить все старые копии
        delete_all_images_with_this_name(old_obj)
  
  def delete(self, *args, **kwargs):
    delete_all_images_with_this_name(self)
    super().delete( *args, **kwargs)

  def url_image_1600_jpg(self):
    return get_small_image_url(self.image.url, '1600', 'jpg')
  def url_image_800_jpg(self):
    return get_small_image_url(self.image.url, '800', 'jpg')
  def url_image_400_jpg(self):
    return get_small_image_url(self.image.url, '400', 'jpg')
  def url_image_70_jpg(self):
    return get_small_image_url(self.image.url, '70', 'jpg')
  def url_image_1600_webp(self):
    return get_small_image_url(self.image.url, '1600', 'webp')
  def url_image_800_webp(self):
    return get_small_image_url(self.image.url, '800', 'webp')
  def url_image_400_webp(self):
    return get_small_image_url(self.image.url, '400', 'webp')
  def url_image_70_webp(self):
    return get_small_image_url(self.image.url, '70', 'webp')
  def url_image_1600_avif(self):
    return get_small_image_url(self.image.url, '1600', 'avif')
  def url_image_800_avif(self):
    return get_small_image_url(self.image.url, '800', 'avif')
  def url_image_400_avif(self):
    return get_small_image_url(self.image.url, '400', 'avif')
  def url_image_70_avif(self):
    return get_small_image_url(self.image.url, '70', 'avif')




class Color(models.Model):
  """Цвета. Простейший справочник"""
  name = models.CharField('Название', max_length=30, unique=True)
  slug = models.SlugField('URL-идентификатор', max_length=40, unique=True, validators=[validate_slug_without_underlines],)
  css_color = models.TextField('css-цвет',  max_length=240) # значение для CSS color. может быть градиентом!
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def html_color(self):
    return mark_safe(f'<div style="width:30px;aspect-ratio:1/1;background: {self.css_color};border-radius: 4px; ">') 
  html_color.short_description = 'html-цвет'

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Цвета'
    verbose_name = 'Цвет'

  def __str__(self):
    return self.name
  


class Country(models.Model):
  """Страны. Простейший справочник"""
  name = models.CharField('Название', max_length=30, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Страны-производители'
    verbose_name = 'Страна-производитель'

  def __str__(self):
      return '%s' % (self.name)


class Material(models.Model):
  """Материалы. Простейший справочник"""
  name = models.CharField('Название', max_length=30, unique=True)
  # icon = models.ImageField('Иконка', upload_to='')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Материалы'
    verbose_name = 'Материал'

  def __str__(self):
    return '%s' % (self.name)



class GeometryForm(models.Model):
  """Формы (тарелок). Простейший справочник"""
  name = models.CharField('Название', max_length=30, unique=True)
  # icon = models.ImageField('Иконка', upload_to='')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Формы'
    verbose_name = 'Форма'

  def __str__(self):
    return '%s' % (self.name)



class NonstickType(models.Model):
  """Типы антипригарного покрытия. Простейший справочник"""
  name = models.CharField('Название', max_length=40, unique=True)
  # icon = models.ImageField('Иконка', upload_to='')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    get_latest_by = ['created_at']
    verbose_name_plural = 'Типы антипригарных покрытий'
    verbose_name = 'Тип антипригарного покрытия'

  def __str__(self):
    return '%s' % (self.name)