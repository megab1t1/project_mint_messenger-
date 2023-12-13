from django import template

register = template.Library()


@register.inclusion_tag('mint/user_card.html')
def get_card(u):
    return {'u': u}


@register.inclusion_tag('mint/message_template.html')
def message(m):
    return {'m': m}

