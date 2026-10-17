"""Formulários da empresa logada."""
from django import forms

from .models import Customer, Product, Sale, SaleItem


class SaleItemForm(forms.ModelForm):
    """Novo item de venda: venda, produto, quantidade e preço."""

    class Meta:
        model = SaleItem
        fields = ["sale", "product", "quantity", "price"]

    def __init__(self, *args, company, **kwargs):
        super().__init__(*args, **kwargs)
        # o queryset nasce a cada requisição, com a empresa de quem está logado (nunca no import do módulo)
        self.fields["sale"].queryset = Sale.all_objects.filter(company=company)
        self.fields["product"].queryset = Product.all_objects.filter(company=company)


class CustomerForm(forms.ModelForm):
    """Cadastro de cliente."""

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        # a UniqueConstraint tem "company", que não está no form: o Django pula essa validação e o banco estoura
        email = self.cleaned_data["email"]
        if Customer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Já existe um cliente com este e-mail.")
        return email
