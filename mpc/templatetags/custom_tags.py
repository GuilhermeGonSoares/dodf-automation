from django import template
from datetime import datetime

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def get_item_by_secao(array, secao):
    return array.filter(secao=secao)


@register.filter
def get_formated_data(value):
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        return value