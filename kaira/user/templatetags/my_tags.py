from django import template

register = template.Library()

@register.simple_tag
def calc_discount( actual_price, discount ):
    return actual_price-(actual_price *(discount/100))

@register.simple_tag
def calc_subtotal(actual_price, discount ,quantity):
    return (actual_price-(actual_price *(discount/100)) )* quantity
    
    