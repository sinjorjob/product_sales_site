from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from ec_site.models import OrderItem, OrderItemDetail
from django.utils.timezone import datetime
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .forms import OrderFilterForm, OrderItemForm
from django_filters.views import FilterView
from .filters import OrderFilter
from django.urls import reverse_lazy
from django.db.models import Sum
from ec_site.models import *
from django_pandas.io import read_frame
import pandas as pd
import plotly.express as px


class Dashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'sales_management/dashboard.html')

    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()


class UnshippedOrder(LoginRequiredMixin, UserPassesTestMixin, ListView):
    
    model = OrderItem
    paginate_by = 5
    template_name = "sales_management/shukka.html"

    def get_queryset(self):

        queryset = OrderItem.objects.filter(is_shipped=False)
        return queryset

    def get_context_data(self, **kwargs):
        

        context = super(UnshippedOrder, self).get_context_data(**kwargs)
        today = datetime.today()
        today_orders = OrderItem.objects.filter(created_on__year=today.year, 
          created_on__month=today.month, created_on__day=today.day,is_shipped=False) 
        
        all_orders = OrderItem.objects.filter(is_shipped=False)
        total_revenue = 0
        unshipped_orders = []  #未出荷の注文を格納
        for order in today_orders:
            total_revenue += order.price
            if not order.is_shipped:
                unshipped_orders.append(order)
        #現在日付の取得
        today = today.strftime('%Y/%m/%d')
        print("today=",today)
        
        #context['orders'] = unshipped_orders
        context['total_revenue'] = total_revenue
        context['total_orders'] = len(today_orders)
        context['unshipped_total_orders'] = len(all_orders)
        context['form'] = OrderFilterForm()
        context['today'] = today
        return context

    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()


class OrderDetails(LoginRequiredMixin,UserPassesTestMixin, TemplateView):

    def get(self, request, pk, *args, **kwargs):
        #注文データの取得
        order = OrderItem.objects.get(pk=pk)
        #注文明細データの取得
        order_details = OrderItem.objects.get(pk=pk).orderitemdetail_set.all()
        context = {'order': order, 'order_details':order_details}
        return render(request, 'sales_management/shukka-detail.html', context)
    
    
    def post(self, request, pk, *args, **kwargs):
        order = OrderItem.objects.get(pk=pk)
        order.is_shipped = True
        order.save()
        
        context = {'order': order}
        return render(request, 'sales_management/shukka-detail.html', context)

    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()


class OrderListView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    """
    検索後のレコード数を取得するためにFilterViewのgetメソッドをオバーライド
    """
    
    model = OrderItem
    filterset_class = OrderFilter
    paginate_by = 10
    template_name = "sales_management/order_management.html"
    queryset = OrderItem.objects.all().order_by('-created_date')

    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if not self.filterset.is_bound or self.filterset.is_valid() or not self.get_strict():
            self.object_list = self.filterset.qs
        else:
            self.object_list = self.filterset.queryset.none()

        context = self.get_context_data(filter=self.filterset,
                                        object_list=self.object_list,
                                        order_count = len(self.object_list)) #検索後のレコード数を取得
        return self.render_to_response(context)


    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = OrderItem
    template_name = 'sales_management/order_detail.html'

    def get(self, request, *args, **kwargs):

        order_details = OrderItem.objects.get(pk=self.kwargs['pk']).orderitemdetail_set.all()
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, order_details=order_details)
        return self.render_to_response(context)

    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()


class OrderEditView(LoginRequiredMixin,UpdateView, UserPassesTestMixin):

    model = OrderItem
    form_class = OrderItemForm
    template_name = 'sales_management/order_edit.html'
    
    #登録処理が正常終了した場合の遷移先を指定
    success_url = reverse_lazy('update_done')

    def get(self, request, *args, **kwargs):

        order_details = OrderItem.objects.get(pk=self.kwargs['pk']).orderitemdetail_set.all()
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, order_details=order_details)
        return self.render_to_response(context)


    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()


def update_done(request):
    #更新処理が正常終了した場合に呼ばれるテンプレートを指定
    
    return render(request, 'sales_management/update_done.html')


def analysis_screen(request):
    order_items = OrderItem.objects.all()
    df_orders = read_frame(order_items, fieldnames=['created_date', 'price', 'items__name'])
    df_orders.rename(columns={'created_date': '注文日', 'price': '売上金額', 'items__name':'製品名'}, inplace=True)
    #### 円グラフの生成
    fig_pie = px.pie(df_orders, names='製品名', values="売上金額")
    fig_pie.update_layout(
        width=500,  # figureの幅
        height=350,  # figureの高さ
        title={
            "text": "製品毎の売上金額割合",
            # グラフタイトルのスタイル
            "font": {"family": "Courier", "size": 20, "color": "slategray"},
            },
            margin={"l": 20, "r": 20, "t": 40, "b": 20},  # 余白
            paper_bgcolor="lightyellow",  # グラフ領域の背景色
            )
    plot_fig_pie = fig_pie.to_html(fig_pie, include_plotlyjs=True)
    #df_orders['注文日'] = df_orders['注文日'].astype(str)


    #日別の売上金額折れ線グラフ
    order_details = OrderItemDetail.objects.all().order_by('created_date')
    df_order_details = read_frame(order_details, fieldnames=['created_date', 'product', 'product__price', 'quantity'])
    df_order_details.rename(columns={'created_date': '注文日', 'product':'製品名', 'product__price': '単価', 'quantity':'数量'}, inplace=True)
    df_order_details['売上金額'] = df_order_details['単価'] * df_order_details['数量']
    df_order_details['年月'] = pd.to_datetime(df_order_details['注文日']).dt.strftime("%Y-%m")
    #df_order_details['注文日'] = df_orders['注文日'].astype(str)
    fig_line = px.bar(df_order_details, x='注文日', y="売上金額",log_y=True, color="製品名",height=400)
    fig_line.update_xaxes(tickvals=df_orders['注文日'],tickformat="%Y-%m/%d") #軸の値
    fig_line.update_yaxes(tickvals=df_orders['売上金額'],tickformat='0.0f') #軸の値
 
    fig_line.update_layout(
        width=800,  # figureの幅
        height=400,  # figureの高さ
        autosize=True,

        title={
            "text": "日別の売上金額折れ線グラフ",
            # グラフタイトルのスタイル
            "font": {"family": "Courier", "size": 20, "color": "slategray"},
            },
            margin={"l": 20, "r": 20, "t": 40, "b": 20},  # 余白
            paper_bgcolor="lightyellow",  # グラフ領域の背景色
            )

    plot_fig_line = fig_line.to_html(fig_line, include_plotlyjs=True)

    return render(request, 'sales_management/sales_analysis.html',{
        "plot_fig_pie":plot_fig_pie,
        "plot_fig_line":plot_fig_line
        })
