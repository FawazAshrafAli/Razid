from django import template
# from .custom_tags import register



register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)