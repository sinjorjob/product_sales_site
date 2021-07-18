from django_filters import filters
from django_filters import FilterSet
from ec_site.models import OrderItem
from django.utils.timezone import datetime

IS_PAID =(('','すべて'),('True', '支払い済み'), ('False','未払い'))
IS_SHIPPED=(('','すべて'),('True', '出荷済み'), ('False','未出荷'))

ORDER_DATES=(('','すべて')),
order_dates = OrderItem.objects.all().values_list('created_date', flat=True).distinct()
for date in order_dates:
    created_date = date.strftime('%Y-%m-%d')
    ORDER_DATES += ((created_date, created_date)),

CUSTOMERS = (('','すべて')),
customer_list = OrderItem.objects.all().values_list('name', flat=True).distinct()
for customer in customer_list:
    CUSTOMERS += ((customer, customer)),


class OrderFilter(FilterSet):
    is_paid = filters.ChoiceFilter(
        label="支払いステータス", 
        choices=IS_PAID,
        widget=filters.forms.Select(attrs={'class': 'form-select fmxw-200'})
    )
        
    is_shipped = filters.ChoiceFilter(
        label="配送ステータス", 
        choices=IS_SHIPPED,
        widget=filters.forms.Select(attrs={'class': 'form-select fmxw-200'})
        )
    name = filters.ChoiceFilter(
        label="カスタマ名", 
        choices=CUSTOMERS,
        widget=filters.forms.Select(attrs={'class': 'form-select fmxw-200'})
        )
    created_date = filters.ChoiceFilter(
        label="注文日", 
        choices=ORDER_DATES,
        widget=filters.forms.Select(attrs={'class': 'form-select fmxw-200'})
       )

    class Meta:
        model = OrderItem
        fields = ('is_paid','is_shipped', 'name',)

    
