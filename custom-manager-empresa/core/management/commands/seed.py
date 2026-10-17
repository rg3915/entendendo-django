"""Cria três empresas, um usuário em cada e um pouco de dados de vendas."""
from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import Category, Company, Customer, Product, Provider, Sale, SaleItem, User
from core.tenancy import company_scope

DADOS = {
    "Café Aroma": ("regis", [("Café 500 g", "32.90"), ("Cappuccino", "12.50")], ("Ana", "ana@cliente.com")),
    "Pão da Vila": ("bruno", [("Pão de queijo", "4.50"), ("Café 500 g Vila", "29.90")], ("Bia", "bia@cliente.com")),
    "Doce Lar": ("carla", [("Brigadeiro", "3.00"), ("Bolo de pote", "11.00")], ("Caio", "caio@cliente.com")),
}


class Command(BaseCommand):
    help = "Cria três empresas com usuários, produtos, clientes e vendas."

    def handle(self, *args, **options):
        for name, (username, products, (customer_name, email)) in DADOS.items():
            company = Company.objects.create(name=name)
            User.objects.create_user(username, password="demo12345", company=company)
            with company_scope(company):  # fora de uma requisição, a empresa é dita explicitamente
                category = Category.objects.create(company=company, title=f"Geral {name}")
                Provider.objects.create(company=company, name=f"Fornecedor {name}", email=f"compras@{username}.com")
                customer = Customer.objects.create(company=company, first_name=customer_name, email=email)
                sale = Sale.objects.create(company=company, customer=customer)
                for title, price in products:
                    product = Product.objects.create(company=company, title=title, price=Decimal(price), category=category)
                    SaleItem.objects.create(company=company, sale=sale, product=product, quantity=2, price=product.price)
        self.stdout.write(self.style.SUCCESS("3 empresas, 3 usuários (regis, bruno, carla), 6 produtos, 3 vendas."))
