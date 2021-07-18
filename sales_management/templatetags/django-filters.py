from django import template

register = template.Library()
paginate_by = 10


@register.filter(name="page_from")
def page_from(total_orders,page_number):
    page_from = (paginate_by * (page_number - 1)) + 1
    return page_from

@register.filter(name="page_to")
def page_to(total_orders,page_number):
    page_to = (paginate_by * (page_number - 1)) + paginate_by
    if page_to > total_orders:
        page_to = total_orders
    return page_to
