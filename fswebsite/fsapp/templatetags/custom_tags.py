from django import template

register = template.Library()

def get_value(data, key):
    return data.get(key)

register.filter('get_value', get_value)