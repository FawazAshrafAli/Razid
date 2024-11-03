# userapp/templatetags/custom_filters.py
from django import template
from userapp.utils.encryption import encrypt_data

register = template.Library()

@register.filter(name='encrypt')
def encrypt(value):
    try:
        return encrypt_data(value)
    except Exception as e:
        return value  # or handle the error appropriately
