from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('unshipped/', UnshippedOrder.as_view(), name='unshipped_order'),
    path('order/<int:pk>/', OrderDetails.as_view(), name='order-details'),
    path('order_management/', OrderListView.as_view(), name='order_management'),
    path('detail/<int:pk>/', OrderDetailView.as_view(), name="order_detail"),
    path('edit/<int:pk>/', OrderEditView.as_view(), name='order_edit'),
    path('edit_done/', update_done, name='update_done'),
    path('sales_analysis/', analysis_screen, name='analysis'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)