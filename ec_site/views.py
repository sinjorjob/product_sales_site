from django.shortcuts import render, redirect
from django.views import generic
from .models import *
from django.contrib.auth.views import LoginView
from .forms import *
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest 
from django.core.signing import BadSignature, SignatureExpired, dumps, loads 
from django.urls import reverse 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template 
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
import json


class Lp(generic.ListView):
    model = Product
    template_name = 'ec_site/lp.html'
    queryset = Product.objects.all()
    

class ItemList(generic.ListView):
    model = Product
    template_name = 'ec_site/item_list.html'

    def get_queryset(self):
        products = Product.objects.all()
        if 'q' in self.request.GET and self.request.GET['q'] != None:
            q = self.request.GET['q']
            print("q=", q)
            products = products.filter(name__icontains = q)
        return products

    def get_context_data(self, **kwargs):
       context = super(ItemList, self).get_context_data(**kwargs)
       context['category_list'] = Category.objects.all()
       return context

 
class CategoryView(generic.ListView):
    """カテゴリのリンククリック"""

    template_name = 'ec_site/item_list.html'

    def get_queryset(self):
        products = Product.objects.all()
        if 'q' in self.request.GET and self.request.GET['q'] != None:
            q = self.request.GET['q']
            print("q=", q)
            products = products.filter(name__icontains = q)
        else:
            """カテゴリでの絞り込み"""
            category_name = self.kwargs['category']
            self.category_name = Category.objects.get(name=category_name)
            products = Product.objects.filter(category=self.category_name)
        return products

    def get_context_data(self, **kwargs):
       context = super(CategoryView, self).get_context_data(**kwargs)
       context['category_list'] = Category.objects.all()
       return context


class ItemDetail(generic.DetailView):
    model = Product
    template_name = 'ec_site/item_detail.html'


    def get_context_data(self, **kwargs):
       context = super(ItemDetail, self).get_context_data(**kwargs)
       context['category_list'] = Category.objects.all()
       return context


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'ec_site/login.html'


class SignUp(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'ec_site/sign_up.html'
    form_class = SignUpForm
   
    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        """
        get_template　→ temptate.render(context)

        テンプレートファイルを読み込みんでからコンテキストを注入する処理になっております。
        ここでセットしたコンテキスト(辞書型のオブジェクト)はテンプレート側から{{ xxx }}
        のようにアクセスできる。
        """
        subject_template = get_template('ec_site/mail_template/sign_up/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('ec_site/mail_template/sign_up/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        messages.success(self.request, '本登録用リンクを送付しました')
        return  HttpResponseRedirect(reverse('ec_site:sign_up_confirm'))


class SignUpDone(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'ec_site/sign_up_done.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内


    """
    getメソッドは、クライアントからこのビューに対してHTTP GETが送られた際に実行される関数
    URLについているトークンが一定時間以内に生成されたものかを検証し、正当であると判断したらテンプレート表示、
    正しくなければ(時間切れ等)HTTPエラーを返すようにカスタマイズ
    全て正常に処理が進んだ場合はsuper().get(request, **kwargs)で親クラスのgetメソッドを呼んでいる)
    """
    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    
                    # [7-1]追加 ここから
                    # ユーザ処理完了後にそのユーザにひもづくカートも生成
                    his_cart = ShoppingCart()
                    his_cart.user = user
                    his_cart.save()
                    
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

class SignUpComfirm(generic.TemplateView):
    """ユーザ登録確認画面"""
    template_name = 'ec_site/sign_up_confirm.html'


class ShoppingCartDetail(LoginRequiredMixin, generic.DetailView):
    model = ShoppingCart
    template_name = "ec_site/shopping_cart.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['form'] = ShoppingCartDetailForm()
        return self.render_to_response(context)
        
        
    def post(self, request, *args, **kwargs):

        if 'product_pk' in self.request.POST and self.request.POST['product_pk'] != None:

            user = request.user
            product_pk = request.POST.get('product_pk')
            product = Product.objects.get(pk = product_pk)
            amount = request.POST.get('amount')

            exist = ShoppingCartItem.objects.filter(cart__user = user).filter(product = product)

            # すでにカートに存在する商品の場合は個数をインクリメント
            if len(exist) > 0:
                current_amount = exist[0].amount
                exist[0].amount = current_amount + int(amount)
                exist[0].save()
            else:
                new_cart_item = ShoppingCartItem()
                new_cart_item.cart = request.user.cart
                new_cart_item.product = product
                new_cart_item.amount = int(amount)
                new_cart_item.save()
            return HttpResponseRedirect(reverse('ec_site:cart',  kwargs={'pk': self.get_object().pk}))
        
        if 'name' in self.request.POST and self.request.POST['name'] != None:
            #注文画面下部のフォームで入力されたユーザ情報を取得
            name = request.POST.get('name')
            email = request.POST.get('email')
            address = request.POST.get('address')
            zip_code = request.POST.get('zip_code')

            #注文データを生成 
            order = OrderItem.objects.create(
                user=User.objects.get(email=request.user.cart),
                name=name,
                email=email,
                address=address,
                zip_code=zip_code
                )

            #order_items = {'items': []}  #オーダー情報の格納辞書
            cart_items = ShoppingCartItem.objects.filter(cart__user__email=request.user.cart)
            #オーダーデータに紐づく明細データを生成
            for item in cart_items:
                OrderItemDetail.objects.create(
                            invoice = OrderItem.objects.get(pk= order.pk),
                            product = item.product,
                            #unit_price = item.product.price,
                            quantity = item.amount 
                          )

            cart_datas = ShoppingCart.objects.filter(user = User.objects.get(email=request.user.cart))
            total_price = [data.total_price for data in cart_datas]

            order_items = {'items': []}  #オーダー情報の格納辞書
            for item in cart_items:
                item_data = {
                    'id': item.product.pk,
                    'name': item.product,
                    }
                order_items['items'].append(item_data)

            item_ids = []
            #製品名のPKを取得
            for item in order_items['items']:
                item_ids.append(item['id'])
            #注文データに商品情報を追加
            order.items.add(*item_ids)
            order.price = total_price[0]
            order.save()

            #return  HttpResponseRedirect(reverse('ec_site:sign_up_confirm'))
            return redirect('ec_site:order-confirmation', pk=order.pk)


class OrderConfirmation(generic.TemplateView):

    def get(self, request, pk, *args, **kwargs):
        order = OrderItem.objects.get(pk=pk)
        order_details = OrderItem.objects.get(pk= pk).orderitemdetail_set.all()
        print("order=", order)
        context = {
            'title': '注文日時：' + order.created_on.strftime('%Y/%m/%d %H:%M:%S'),
            'pk': order.pk,
            'items': order.items.all(),
            'price': order.price,
            'order_details': order_details
        }
        return render(request, 'ec_site/order_confirmation.html', context)


    def post(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)
        print("postメソッドが呼ばれました")

        #注文データのisPaidをTrueに更新
        if data['isPaid']:
            print("if data!!")
            order = OrderItem.objects.get(pk=pk)
            order.is_paid = True
            order.save()
        #カートの中身を空にする
        cart_items = ShoppingCartItem.objects.filter(cart__user__email=request.user.cart)
        cart_items.delete()
        return redirect('ec_site:payment-confirmation')

def update_cart_item_amount(request):

    cart_item_pk = request.POST.get('cart_item_pk')
    new_amount = request.POST.get('amount')

    if cart_item_pk == None or new_amount == None:
        return JsonResponse({'error': 'invalid parameter'})
    if int(new_amount) <= 0:
        return JsonResponse({'error': 'amount must be greater than zero'})
    
    try:
        cart_item = ShoppingCartItem.objects.get(pk = cart_item_pk)
        cart_item.amount = int(new_amount)
        cart_item.save()
        print(cart_item.amount)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e.args)})

    
def delete_cart_item(request):
    
    cart_item_pk = request.POST.get('cart_item_pk')
    if cart_item_pk == None:
        return JsonResponse({'error': 'invalid parameter'})
    try:
        cart_item = ShoppingCartItem.objects.get(pk = cart_item_pk)
        cart_item.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e.args)})


class OrderPayConfirmation(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'ec_site/order_pay_confirmation.html')