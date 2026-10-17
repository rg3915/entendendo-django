"""Telas da empresa logada: produtos, novo item de venda e painel."""
import asyncio

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import SaleItemForm
from .models import Product, SaleItem


@login_required
def product_list(request):
    """Produtos e preços da empresa do usuário."""
    return render(request, "core/product_list.html", {"products": Product.objects.all()})


@login_required
def sale_item_create(request):
    """Novo item de venda."""
    form = SaleItemForm(request.POST or None, company=request.user.company)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.company = request.user.company
        item.save()
        return redirect("product_list")
    return render(request, "core/sale_item_form.html", {"form": form})


@login_required
def dashboard(request):
    """Total vendido, guardado no cache por 5 minutos."""
    key = f"sales_total:{request.user.company_id}"  # a chave do cache leva a empresa
    total = cache.get(key)
    if total is None:
        total = SaleItem.objects.aggregate(total=Sum(F("price") * F("quantity")))["total"] or 0
        cache.set(key, total, 300)
    return render(request, "core/dashboard.html", {"total": total})


async def products_async(request):
    """Versão assíncrona da lista: espera um pouco (uma chamada externa, por exemplo) e consulta o banco."""
    await asyncio.sleep(0.2)
    titles = [product.title async for product in Product.objects.all()]
    return JsonResponse({"user": request.user.username, "products": titles})
