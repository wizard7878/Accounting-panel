from django import template

register = template.Library()

@register.filter(name='persian_int')
def persian_int(english_int):
    persian_nums = {'0':'۰', '1':'۱', '2':'۲', '3':'۳', '4':'۴', '5':'۵', '6':'۶', '7':'۷', '8':'۸', '9':'۹'}
    number = str(english_int)
    persian_dict = number.maketrans(persian_nums)
    result = number.translate(persian_dict)
    return result

@register.filter(name='split_three_digits')
def split_three_digits(value):
    if not isinstance(value, str):
        value = str(value)
    return ','.join([value[max(i-3, 0):i] for i in range(len(value), 0, -3)][::-1])


@register.filter
def to_str(value):
    """converts int to string"""
    return str(value)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)