from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET
from .models import *
   

  
def index(request):
  return render(request, 'shop/filler.html')
 


def about(request):
  return HttpResponse("О сайте")
 


def contact(request):
  return HttpResponse("контакты")
 


def privacy(request):
  return HttpResponse("Политика Конфиденциальности")
 


def delivery(request):
  return HttpResponse("Доставка")
 


def payment(request):
  return HttpResponse("Оплата")



@require_GET
def robots(request):
  lines = [
      "User-Agent: *",
      "Disallow: /",
  ]
  return HttpResponse("\n".join(lines), content_type="text/plain")



def base_categories(request):
  categories = Category.objects.filter(parent_category = None)
  viewCollections = Collection.objects.all()
  breadcrumbs = [{"title": "Главная","link": reverse('home')}, {"title": "Категории", "link": reverse('base_categories')}]

  data = {"viewCategories": categories,}
  data["breadcrumbs"] = breadcrumbs
  data["viewCollections"] = viewCollections

  return render(request, 'shop/categories.html', data)
 


def category(request, category):
  cat = get_object_or_404(Category, slug=category)  
  data = {}
  data["category"] = cat
  breadcrumbs = [{"title": "Главная", "link": reverse('home')}, {"title": "Категории", "link": reverse('base_categories')}]

  if(not(cat.parent_category)):
    childCats = cat.category_set.all()
    breadcrumbs.append({"title": cat.name, "link": cat.get_absolute_url()})

    data["viewCategories"] = childCats
    data["breadcrumbs"] = breadcrumbs

    return render(request, 'shop/categories.html', data)
  
  else:
    productVariants = ProductVariant.objects.filter(color_of_base_product__base_product__category__slug = category)
    viewCollections = Collection.objects.filter(products__category = cat).distinct()
    breadcrumbs.append({"title": cat.parent_category.name, "link": cat.parent_category.get_absolute_url()})
    breadcrumbs.append({"title": cat.name, "link": cat.get_absolute_url()})

    data["viewProductVariants"] = productVariants
    data["viewCollections"] = viewCollections
    data["breadcrumbs"] = breadcrumbs

    return render(request, 'shop/products_byCategory.html', data)



def main_collections(request):
  collections = Collection.objects.all()
  data = {}

  breadcrumbs = [{"title": "Главная", "link": reverse('home')}, {"title": "Коллекции", "link": reverse('main_collections')}]

  data["breadcrumbs"] = breadcrumbs
  data["viewCollections"] = collections

  return render(request, 'shop/collections.html', data)




def collection(request, collection):
  collectionNow = get_object_or_404(Collection, slug=collection) 
  data = {}
  data["collection"] = collectionNow

  productVariants = ProductVariant.objects.filter(color_of_base_product__base_product__collection__slug = collection)
  breadcrumbs = [{"title": "Главная", "link": reverse('home')}, {"title": "Коллекции", "link": reverse('main_collections')}]
  breadcrumbs.append({"title": collectionNow.name, "link": collectionNow.get_absolute_url()})

  data["viewProductVariants"] = productVariants
  data["breadcrumbs"] = breadcrumbs

  return render(request, 'shop/products_byCollection.html', data)
 


def base_product(request, category, base_product):
  baseProduct = get_object_or_404(BaseProduct, slug=base_product)
  categoryNow = get_object_or_404(Category, slug=category)
  colorsOfProduct = baseProduct.colors.all().distinct()

  productVariants = ProductVariant.objects.filter(color_of_base_product__base_product__slug = base_product)
  baseProductImages = BaseProductImg.objects.filter(base_product__slug = base_product)
  productVariantsImages = ProductVariantImg.objects.filter(product_variant__color_of_base_product__base_product__slug = base_product)

  data = {}

  breadcrumbs = [{"title": "Главная", "link": reverse('home')}, {"title": "Категории", "link": reverse('base_categories')}]
  breadcrumbs.append({"title": categoryNow.parent_category.name, "link": categoryNow.parent_category.get_absolute_url()})
  breadcrumbs.append({"title": categoryNow.name, "link": categoryNow.get_absolute_url()})
  breadcrumbs.append({"title": baseProduct.name, "link": baseProduct.get_absolute_url()})

  data["baseProduct"] = baseProduct
  data["colorsOfProduct"] = colorsOfProduct
  data["productVariants"] = productVariants
  data["baseProductImages"] = baseProductImages
  data["productVariantsImages"] = productVariantsImages
  data["breadcrumbs"] = breadcrumbs

  print(baseProductImages)
  print(productVariantsImages)

  return render(request, 'shop/product.html', data)
 


def color_of_base_product(request, category, base_product, color_of_base_product):
  return HttpResponse(f"<h1>цвет базового продукта</h1> Категория: {category}<br/> Базовый продукт: {base_product}<br/> Цвет: {color_of_base_product}") 



def product_variant(request,category, base_product, color_of_base_product, product_variant):
  return HttpResponse(f"<h1>Вариант цвета базового продукта</h1> Категория: {category}<br/> Базовый продукт: {base_product}<br/> Цвет: {color_of_base_product}<br/> Вариант продукта: {product_variant}") 




# 4xx - ошибки

def page_not_found(request, exception):
  return HttpResponseNotFound("страница не найдена : ")
# а ещё можно 301-редирект вместо 404-й  return redirect('home', permanent = True)