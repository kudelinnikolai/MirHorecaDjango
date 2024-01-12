from django import template
import shop.views as views



register = template.Library()


# чтобы использовать описанные здесь теги, в нужном шаблоне необходимо написать {% load shop-tags %}
# @register.simple_tag()  #регистрируем простой тег
# @register.inclusion_tag()  #регистрируем включающий тег


