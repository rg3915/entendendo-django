from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Company, CompanyModel, Customer, Product, Provider, Sale, SaleItem, User


class CompanyAdmin(admin.ModelAdmin):
    """Superusuário vê todas as empresas; os outros, só a própria (o Manager já filtra)."""

    def get_queryset(self, request):
        if request.user.is_superuser:
            return self.model.all_objects.all()
        return super().get_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser and issubclass(db_field.related_model, CompanyModel):
            kwargs["queryset"] = db_field.related_model.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(CompanyAdmin):
    inlines = (SaleItemInline,)
    list_display = ("__str__", "customer", "company")


@admin.register(Product)
class ProductAdmin(CompanyAdmin):
    list_display = ("title", "price", "company")


admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register([Customer, Provider, Category], CompanyAdmin)
