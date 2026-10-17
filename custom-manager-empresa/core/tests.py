"""Testes de isolamento: uma empresa nunca enxerga os dados da outra."""
import re
from decimal import Decimal

from django.apps import apps
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from .forms import CustomerForm, SaleItemForm
from .models import Category, Company, CompanyModel, Customer, Product, Provider, Sale, SaleItem, User
from .tenancy import company_scope


class IsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = {}
        for name, username, product in [("Café Aroma", "regis", "Café 500 g"), ("Pão da Vila", "bruno", "Pão de queijo")]:
            company = Company.objects.create(name=name)
            user = User.objects.create_user(username, password="x", company=company)
            with company_scope(company):
                category = Category.objects.create(title="Geral")
                Provider.objects.create(name="Fornecedor", email="compras@fornecedor.com")
                customer = Customer.objects.create(first_name="Ana", email="ana@cliente.com")
                sale = Sale.objects.create(customer=customer)
                prod = Product.objects.create(title=product, price=Decimal("10"), category=category)
                SaleItem.objects.create(sale=sale, product=prod, quantity=2, price=prod.price)
            cls.data[username] = {"company": company, "user": user, "product": prod, "sale": sale}
        cls.cafe, cls.vila = cls.data["regis"]["company"], cls.data["bruno"]["company"]
        cls.admin = User.objects.create_superuser("admin", password="x")

    def setUp(self):
        cache.clear()

    def test_fora_da_requisicao_nao_aparece_nada(self):
        self.assertFalse(Product.objects.exists())

    def test_cada_empresa_ve_so_os_seus_dados_em_todos_os_modelos(self):
        models = [m for m in apps.get_app_config("core").get_models() if issubclass(m, CompanyModel)]
        with company_scope(self.cafe):
            for model in models:
                with self.subTest(model=model.__name__):
                    self.assertTrue(model.objects.exists())
                    self.assertFalse(model.objects.exclude(company=self.cafe).exists())

    def test_contexto_some_depois_da_requisicao(self):
        self.client.force_login(self.data["regis"]["user"])
        self.client.get("/")
        self.assertFalse(Product.objects.exists())

    async def test_view_async_usa_a_empresa_da_requisicao(self):
        await self.async_client.aforce_login(self.data["regis"]["user"])
        response = await self.async_client.get("/async/produtos/")
        self.assertEqual(response.json()["products"], ["Café 500 g"])

    def test_form_lista_so_os_produtos_da_empresa_mesmo_depois_de_outra(self):
        for username in ["bruno", "regis"]:
            self.client.force_login(self.data[username]["user"])
            html = self.client.get("/itens/novo/").text
            options = re.findall(r"<option[^>]*>([^<]*)</option>", html)
        self.assertIn("Café 500 g", options)
        self.assertNotIn("Pão de queijo", options)

    def test_post_com_produto_de_outra_empresa_e_recusado(self):
        form = SaleItemForm(data={"sale": self.data["regis"]["sale"].pk, "product": self.data["bruno"]["product"].pk,
                                  "quantity": 1, "price": 1}, company=self.cafe)
        self.assertFalse(form.is_valid())
        self.assertIn("product", form.errors)

    def test_fk_de_outra_empresa_nao_salva(self):
        with company_scope(self.cafe), self.assertRaises(ValidationError):
            SaleItem.objects.create(sale=self.data["regis"]["sale"], product=self.data["bruno"]["product"], quantity=1, price=1)

    def test_nao_salva_registro_de_outra_empresa(self):
        product = self.data["bruno"]["product"]
        with company_scope(self.cafe), self.assertRaises(PermissionDenied):
            product.save()

    def test_email_unico_por_empresa(self):
        with company_scope(self.vila):
            form = CustomerForm(data={"first_name": "Ana 2", "email": "ana@cliente.com"})
            self.assertEqual(form.errors["email"], ["Já existe um cliente com este e-mail."])

    def painel(self, username):
        self.client.force_login(self.data[username]["user"])
        return re.search(r"<h2>(.*?)</h2>", self.client.get("/painel/").text).group(1)

    def test_cache_do_painel_e_por_empresa(self):
        with company_scope(self.vila):
            SaleItem.objects.create(sale=self.data["bruno"]["sale"], product=self.data["bruno"]["product"], quantity=1, price=5)
        self.assertEqual(self.painel("regis"), "R$ 20.00")
        self.assertEqual(self.painel("bruno"), "R$ 25.00")

    def test_superusuario_ve_todas_as_empresas_no_admin(self):
        self.client.force_login(self.admin)
        self.assertIn("2 produtos", self.client.get("/admin/core/product/").text)
