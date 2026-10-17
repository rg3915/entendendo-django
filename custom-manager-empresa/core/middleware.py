"""Middleware que define a empresa do usuário logado durante a requisição."""
from .tenancy import company_scope


class CompanyMiddleware:
    """Precisa vir depois do AuthenticationMiddleware, que cria o request.user."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with company_scope(getattr(request.user, "company", None)):
            return self.get_response(request)
