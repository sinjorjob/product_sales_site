from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import F, Sum 


class Category(models.Model):
    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = "カテゴリ"
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = "商品"

    thumbnail = models.ImageField(verbose_name = 'サムネイル', upload_to = "thumbnails/")
    name = models.CharField(verbose_name = '製品名', max_length=150, null = False, blank=False)
    price = models.IntegerField(verbose_name = '価格')
    description = models.TextField(verbose_name = '説明')
    category = models.ForeignKey(Category, on_delete = models.PROTECT,verbose_name ="カテゴリ")

    def __str__(self):
        return self.name


class MyUserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'ユーザ'
        verbose_name_plural = 'ユーザ'

    """カスタムユーザーモデル."""
    email = models.EmailField('メールアドレス', max_length=150, null = False, blank=False, unique = True)
    name = models.CharField('名前', max_length=150, null = False, blank=False)
    
    is_staff = models.BooleanField(
        '管理者',
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        '有効',
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email


class ShoppingCart(models.Model):

    class Meta:
        verbose_name = 'ショッピングカート'
        verbose_name_plural = 'ショッピングカート'

    user = models.OneToOneField(User,verbose_name = 'ユーザ', related_name = 'cart',on_delete = models.CASCADE)

    @property
    def item_count(self):
        return self.cart_items.all().aggregate(amount = Sum('amount'))['amount']

    @property
    def total_price(self):
        return self.cart_items.all().aggregate(total=Sum(F('product__price') * F('amount')))['total']

    def __str__(self):
        return str(self.user)


class ShoppingCartItem(models.Model):
    class Meta:
        verbose_name = 'ショッピングカートアイテム'
        verbose_name_plural = 'ショッピングカートアイテム'

    cart = models.ForeignKey(
        ShoppingCart,
        related_name = 'cart_items',
        verbose_name = 'ショッピングカート',
        on_delete = models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name = '数量'
    )
    def __str__(self):
        return str(self.cart)

class OrderItem(models.Model):
    class Meta:
        verbose_name = '注文データ'
        verbose_name_plural = '注文データ'

    user = models.ForeignKey(User,verbose_name = 'ユーザ',on_delete = models.CASCADE, null=True)
    items = models.ManyToManyField('Product', related_name='order', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_date = models.DateField(auto_now_add=True)
    price = models.DecimalField(verbose_name="合計金額",max_digits=7, decimal_places=0, null=True, blank=True)
    name = models.CharField(verbose_name="氏名", max_length=50, blank=True)
    email = models.EmailField(verbose_name="メールアドレス",max_length=50, blank=True)
    address = models.CharField('住所', max_length=255, null=True, blank=True)
    zip_code = models.IntegerField(verbose_name="郵便番号",blank=True, null=True)
    is_paid = models.BooleanField(verbose_name="支払い済みフラグ", default=False)
    is_shipped = models.BooleanField(verbose_name="出荷済みフラグ", default=False)

    def __str__(self):
        return f'注文: {self.created_on.strftime("%b %d %Y %I:%M %p")}'


class OrderItemDetail(models.Model):
    class Meta:
        verbose_name = '注文明細'
        verbose_name_plural = '注文明細'

    invoice = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,verbose_name='商品',on_delete=models.CASCADE)
    #unit_price = models.IntegerField(verbose_name='単価')
    quantity = models.IntegerField(verbose_name='数量')
    created_date = models.DateField(auto_now_add=True)
