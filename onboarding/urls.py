from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.ProductAPIView.as_view(),name='product'),
    path('import_product/', views.ProductUploadAPIView.as_view(),name='import_product'),
    path('category/', views.CategoryAPIView.as_view(),name='category'),
    path('export_csv_template',views.ExportCSVTemplateAPIView.as_view(),name='export_csv_template'),

    path('add_product/', views.add_product, name='add_product'),
    path('product_creation/', views.product_creation, name='product_creation'),





]
