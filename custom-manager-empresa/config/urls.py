from django.contrib import admin
from django.urls import include, path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.product_list, name="product_list"),
    path("itens/novo/", views.sale_item_create, name="sale_item_create"),
    path("painel/", views.dashboard, name="dashboard"),
    path("async/produtos/", views.products_async, name="products_async"),
]
