from django import forms
from django.utils.timezone import datetime
from ec_site.models import OrderItem


ORDER_DATES = (('','すべて'),)
today = datetime.today()
order_dates = OrderItem.objects.filter(is_shipped=False).values_list('created_date', flat=True).distinct()

for date in order_dates:
    ORDER_DATES += ((date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))),


class OrderFilterForm(forms.Form):
    created_date = forms.ChoiceField(
        label='注文日',
        widget=forms.Select(attrs={'class':'form-select fmxw-200'}),
        choices=ORDER_DATES,
        required=True,
    )


class OrderItemForm(forms.ModelForm):
    """
    注文データの編集フォームの定義
    """
    class Meta:
        model = OrderItem
        fields =['name', 'email','address','zip_code','is_shipped']
    
   