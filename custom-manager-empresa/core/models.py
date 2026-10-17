"""Vendas de três empresas no mesmo banco: cada registro tem a sua empresa."""
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models

from .managers import CompanyManager
from .tenancy import get_current_company


class Company(models.Model):
    """A empresa dona dos dados."""

    name = models.CharField("nome", max_length=255)

    class Meta:
        verbose_name = "empresa"

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Usuário do sistema: muitos usuários para uma empresa."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="users", null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.company or 'sem empresa'})"


class TimeStampedModel(models.Model):
    """Datas de criação e de alteração."""

    created = models.DateTimeField("criado em", auto_now_add=True)
    modified = models.DateTimeField("modificado em", auto_now=True)

    class Meta:
        abstract = True


class CompanyModel(TimeStampedModel):
    """Base dos modelos que pertencem a uma empresa."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="empresa")

    objects = CompanyManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def check_same_company(self):
        """Toda FK para outro modelo da empresa precisa apontar para a mesma empresa."""
        for field in self._meta.concrete_fields:
            if field.many_to_one and issubclass(field.related_model, CompanyModel):
                related = getattr(self, field.name)  # a FK direta usa o _base_manager: enxerga todas as empresas
                if related is not None and related.company_id != self.company_id:
                    raise ValidationError({field.name: "Este registro pertence a outra empresa."})

    def clean(self):
        super().clean()
        self.check_same_company()

    def save(self, *args, **kwargs):
        current = get_current_company()
        if self.company_id is None:
            self.company = current
        elif current is not None and self.company_id != current.pk:
            raise PermissionDenied("Este registro pertence a outra empresa.")
        self.check_same_company()
        super().save(*args, **kwargs)


class Customer(CompanyModel):
    """Cliente da empresa."""

    first_name = models.CharField("nome", max_length=100)
    last_name = models.CharField("sobrenome", max_length=255, null=True, blank=True)
    email = models.EmailField("e-mail", max_length=50)

    class Meta:
        ordering = ("first_name",)
        verbose_name = "cliente"
        constraints = [models.UniqueConstraint(fields=["company", "email"], name="customer_email_por_empresa")]

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Provider(CompanyModel):
    """Fornecedor da empresa."""

    name = models.CharField("nome", max_length=100)
    email = models.EmailField("e-mail", max_length=50)

    class Meta:
        ordering = ("name",)
        verbose_name = "fornecedor"
        verbose_name_plural = "fornecedores"
        constraints = [models.UniqueConstraint(fields=["company", "email"], name="provider_email_por_empresa")]

    def __str__(self):
        return self.name


class Category(CompanyModel):
    """Categoria de produto."""

    title = models.CharField("nome", max_length=100)

    class Meta:
        ordering = ("title",)
        verbose_name = "categoria"
        constraints = [models.UniqueConstraint(fields=["company", "title"], name="category_title_por_empresa")]

    def __str__(self):
        return self.title


class Product(CompanyModel):
    """Produto com o preço da empresa."""

    title = models.CharField("nome", max_length=100)
    price = models.DecimalField("preço", max_digits=7, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="categoria", related_name="products")
    providers = models.ManyToManyField(Provider, verbose_name="fornecedores", blank=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "produto"
        constraints = [models.UniqueConstraint(fields=["company", "title"], name="product_title_por_empresa")]

    def __str__(self):
        return self.title


class Sale(CompanyModel):
    """Venda para um cliente."""

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="cliente", related_name="sales")

    class Meta:
        ordering = ("-pk",)
        verbose_name = "venda"

    def __str__(self):
        return f"{self.pk:03d}"


class SaleItem(CompanyModel):
    """Item da venda, com o preço do momento."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name="venda", related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="produto", related_name="sale_items")
    quantity = models.PositiveIntegerField("quantidade")
    price = models.DecimalField("preço de venda", max_digits=7, decimal_places=2)

    class Meta:
        ordering = ("pk",)
        verbose_name = "item da venda"

    def __str__(self):
        return f"{self.pk:03d} - {self.sale}"
