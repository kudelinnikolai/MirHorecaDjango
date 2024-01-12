from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import *

# Register your models here.



class CustomUserAdmin(UserAdmin):
    model = get_user_model()

admin.site.register(get_user_model(), CustomUserAdmin) 



class BaseProductImgInline(admin.TabularInline):
    extra = 1
    model = BaseProductImg
    readonly_fields = ('id', 'get_html_image',)
    list_display = ['get_html_image', 'alt'  , 'image']

class ColorOfProductImgInline(admin.TabularInline):
    extra = 1
    model = ColorOfProductImg
    readonly_fields = ('id', 'get_html_image',)
    list_display = ['get_html_image',  'alt'  , 'image']

class ProductVariantImgInline(admin.TabularInline):
    extra = 1
    model = ProductVariantImg
    readonly_fields = ('id', 'get_html_image',)
    list_display = ['get_html_image', 'alt'  , 'image']

class ColorInline(admin.TabularInline):
    extra = 1
    model = ColorsOfBaseProduct
    show_change_link = True
    list_display_links = ['id']
    fields = ['id','base_product','color']

class ProductVariantInline(admin.TabularInline):
    extra = 1
    model = ProductVariant
    show_change_link = True


@admin.register(BaseProduct) # можно использовать такой вот декоратор для регистрации модели
class BaseProductAdmin(admin.ModelAdmin):  
  # -------------ПОЛЬЗОВАТЕЛЬСКИЕ МЕТОДЫ----------------
  def get_all_variants(self, object):
    
    pass # хочу получить все варианты для данного товара и мб их фото
 
  # -------------ОПРЕДЕЛЕНИЕ СВОЙСТВ КЛАССА----------------

  # Как будет выглядить страница добавления / изменения
  fieldsets = (
    (None, {
      'fields': ('name',  'description', 'slug',  'category', 'collection',
                 'country', 'material', 'geometry_form', 'nonstick_type', 'is_for_dishwasher','is_for_microvawe',)
    }),
    ('Совместимость с плитами', {
      'classes': ('collapse',),
      'fields': (
        ( 'is_for_gas_stoves'),
        ('is_for_electric_stoves','is_for_glass_ceramic_stoves'),
        ('is_for_induction_stoves','is_for_oven'),
        ('is_for_halogen_burners','is_for_open_fire')),
    }),
  )

  # Что отображено на странице со списком объектов:
  list_display = ('id', 'name', 'description', 'slug',  'category', 'collection',
                  'country', 'material', 'geometry_form', 'nonstick_type', 'is_for_dishwasher',
                  'is_for_microvawe', 'is_for_gas_stoves', 'is_for_electric_stoves', 'is_for_glass_ceramic_stoves', 
                  'is_for_induction_stoves','is_for_oven', 'is_for_halogen_burners', 'is_for_open_fire',)  
  
  # Какие поля будут ссылкой на редактирование объекта:
  list_display_links = ('id',)
  # Какие поля можно редактировать прям на странице просмотра всего списка объектов:
  list_editable = ('name',  'slug', 'category', 'collection',
                  'country', 'material', 'geometry_form', 'nonstick_type', 'is_for_dishwasher',
                  'is_for_microvawe', 'is_for_gas_stoves', 'is_for_electric_stoves', 'is_for_glass_ceramic_stoves', 
                  'is_for_induction_stoves','is_for_oven', 'is_for_halogen_burners', 'is_for_open_fire',)
  
  # По каким полям можно сделать быструю фильтрацию:
  # list_filter = (...)
  # Сортировка объектов на странице просмотра. Вообще нахер не нужна и её даже лучше специально обнулить
  ordering = [] 
  # Помощь в заполнении полей
  prepopulated_fields = {'slug': ('name', )} # чтобы лепить слаги из кириллицы, нужна библиотека slugify https://proghunter.ru/articles/django-base-2023-automatic-slug-generation-cyrillic-handling-in-django-9
  # Заменить стандартный select на radio для внешних ключей или списков
  # radio_fields = {'material': admin.VERTICAL}
  # по каким полям можно выполнить поиск. Также используется виждетом быстрого поиска при выборе в связанных моделях (autocomplete_fields)
  search_fields = ('name', 'description', 'slug',)
  # в форме создания / изменения в этом поле (с внешним ключом) можно сделать поиск и автодополнение! Чтобы работало, у соответствующих ModelAdmin должно быть search_fields
  # autocomplete_fields = ['category', 'collection', 'country', 'material', 'nonstick_type',]
  # Другой виджет для полей с внешним ключом (открывается через лупу) в новом окне и позволяет ещё удобнее выбрать объект. Тоже есть поиск.
  raw_id_fields = ('category', 'collection', 'country', 'material', 'nonstick_type',)
  # Поля, доступные только для отображения ( без редактирования )
  readonly_fields = ('created_at', 'updated_at')
  # Кнопки сохранения ещё и сверху формы
  save_on_top = True
  # formfield_overrides = {models.TextField: {"widget": RichTextEditorWidget}} /// здесь будем менять обычный инпут для ввода текста на инпут со вводом html-разметки
  # Нужно ли показывать количество записей в базе через count, или показывать по запросу пользователя. Для маленьких баз можно и показать. True по-умолчанию
  # show_full_result_count = False
  list_per_page = 50
  inlines = [ColorInline, BaseProductImgInline]





@admin.register(ColorsOfBaseProduct)
class ColorsOfBaseProductAdmin(admin.ModelAdmin):
  list_display = ('id', 'base_product', 'color', 'created_at', 'updated_at',)
  list_display_links = ('id',)
  list_editable = ('base_product', 'color',)
  ordering = [] 
  search_fields = ('base_product', 'color', )
  readonly_fields = ('created_at', 'updated_at',)
  raw_id_fields = ('base_product',)
  save_on_top = True
  list_per_page = 50
  inlines = [ProductVariantInline, ColorOfProductImgInline]





@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
  list_display = ('id', 'color_of_base_product', 'featureName', 'slug', 'articul', 'extra_color', 'price',
                   'diameter', 'depth', 'height', 'width', 'length', 'value', 'residue', 'created_at', 'updated_at',)
  fieldsets = (
    (None, {
      'fields': ('residue','color_of_base_product', 'featureName', 'slug', 'articul', 'extra_color', 'price',
                   'diameter', 'depth', 'height', 'width', 'length', 'value', )
    }),
  )
  list_display_links = ('id',)
  list_editable = ('color_of_base_product', 'featureName', 'slug', 'articul', 'extra_color', 'price', 'diameter', 'depth', 'height', 'width', 'length', 'value', 'residue',)
  ordering = [] 
  search_fields = ('featureName', 'slug', 'articul', )
  readonly_fields = ('created_at', 'updated_at',)
  prepopulated_fields = {'slug': ('featureName', )}
  raw_id_fields = ('color_of_base_product',)
  save_on_top = True
  list_per_page = 50
  inlines = [ProductVariantImgInline]




@admin.register(BaseProductImg)
class BaseProductImgAdmin(admin.ModelAdmin):
  list_display = ('base_product'  , 'alt'  , 'image'  , 'get_html_image')

  fieldsets = (
    (None, {
      'fields': ('base_product', 'alt','image')
    }),
  )
  list_display = ('id', 'base_product', 'alt', 'image', 'get_html_image')  
  list_display_links = ('id',)
  list_editable = ('base_product', 'alt')
  ordering = [] 
  search_fields = ('alt', 'image', 'base_product',)
  readonly_fields = ('created_at', 'updated_at',)
  list_per_page = 50
  save_on_top = True




@admin.register(ColorOfProductImg)
class ColorOfProductImgAdmin(admin.ModelAdmin):
  list_display = ('color_of_base_product'  , 'alt'  , 'image'  , 'get_html_image')

  fieldsets = (
    (None, {
      'fields': ('color_of_base_product', 'alt','image')
    }),
  )
  list_display = ('id', 'color_of_base_product', 'alt', 'image', 'get_html_image')  
  list_display_links = ('id',)
  list_editable = ('color_of_base_product', 'alt')
  ordering = [] 
  search_fields = ('alt', 'image', 'color_of_base_product',)
  readonly_fields = ('created_at', 'updated_at',)
  list_per_page = 50
  save_on_top = True




@admin.register(ProductVariantImg)
class ProductVariantImgAdmin(admin.ModelAdmin):
  list_display = ('product_variant'  , 'alt'  , 'image'  , 'get_html_image')

  fieldsets = (
    (None, {
      'fields': ('product_variant', 'alt','image')
    }),
  )
  list_display = ('id', 'product_variant', 'alt', 'image', 'get_html_image')  
  list_display_links = ('id',)
  list_editable = ('product_variant', 'alt')
  ordering = [] 
  search_fields = ('alt', 'image', 'product_variant',)
  readonly_fields = ('created_at', 'updated_at',)
  list_per_page = 50
  save_on_top = True




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('id', 'parent_category', 'name', 'slug', 'get_html_image', 'created_at', 'updated_at',)
  fieldsets = (
    (None, {
      'fields': ('parent_category', 'name', 'slug', 'image',)
    }),
  )
  prepopulated_fields = {'slug': ('name', )}
  list_display_links = ('id',)
  list_editable = ('parent_category', 'name', 'slug', )
  ordering = [] 
  search_fields = ('name', 'slug', )
  readonly_fields = ('created_at', 'updated_at',)
  list_per_page = 50
  actions_on_top = False  # Убираем действие из верхней части списка
  actions_on_bottom = False  # Убираем действие из нижней части списка
  save_on_top = True




@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  list_display = ('id',  'name', 'slug', 'get_html_image', 'created_at', 'updated_at',)
  fieldsets = (
    (None, {
      'fields': ( 'name', 'slug', 'image',)
    }),
  )
  prepopulated_fields = {'slug': ('name', )}
  list_display_links = ('id',)
  list_editable = ( 'name', 'slug', )
  ordering = [] 
  search_fields = ('name', 'slug', )
  readonly_fields = ('created_at', 'updated_at',)
  list_per_page = 50
  save_on_top = True




@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
  list_display = ('id',  'name', 'slug','html_color', 'created_at', 'updated_at',)
  fieldsets = (
    (None, {
      'fields': ( 'name', 'slug', 'css_color',)
    }),
  )
  prepopulated_fields = {'slug': ('name', )}
  list_display_links = ('id',)
  list_editable = ( 'name', 'slug',  )
  ordering = [] 
  search_fields = ('name', 'slug', )
  readonly_fields = ('created_at', 'updated_at',)
  list_per_page = 50
  save_on_top = True



admin.site.register(UserReview)
admin.site.register(Adress)
admin.site.register(Order)
admin.site.register(ProductsInOrder)
admin.site.register(Country)
admin.site.register(Material)
admin.site.register(GeometryForm)
admin.site.register(NonstickType)


admin.site.site_title = 'Админ-панель - Мир HoReCa'
admin.site.site_header ='Админ-панель - Мир HoReCa'
