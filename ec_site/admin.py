from django.contrib import admin
from .models import Category, Product, User, ShoppingCartItem, ShoppingCart, OrderItem, OrderItemDetail

class ProductAdmin(admin.ModelAdmin):
    list_display=('pk','name','price','description', 'category')

class CategoryAdmin(admin.ModelAdmin):
    list_display=('pk','name')

class UserAdmin(admin.ModelAdmin):
    list_display=('pk','email', 'name','is_staff', 'is_active', )

class ShoppingCartItemAdmin(admin.ModelAdmin):
    list_display=('pk','cart','product','amount')

class ShoppingCartAdmin(admin.ModelAdmin):
    list_display=('pk','user')

class InvoiceDetailInline(admin.TabularInline):
    model = OrderItemDetail
    extra = 0

class OrderItemAdmin(admin.ModelAdmin):
    list_display=('pk', 'user', 'created_on', 'created_date', 'price','is_paid', 'is_shipped')
    inlines = [InvoiceDetailInline]

class OrderItemDetailAdmin(admin.ModelAdmin):
    list_display=('pk', 'invoice', 'product','quantity','created_date')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ShoppingCartItem, ShoppingCartItemAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderItemDetail, OrderItemDetailAdmin)
