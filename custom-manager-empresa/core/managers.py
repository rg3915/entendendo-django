"""Manager que filtra tudo pela empresa atual."""
from django.db import models

from .tenancy import get_current_company


class CompanyQuerySet(models.QuerySet):
    def for_company(self, company):
        """Filtro explícito por empresa (para scripts e relatórios)."""
        return self.filter(company=company)


class CompanyManager(models.Manager.from_queryset(CompanyQuerySet)):
    """Toda consulta passa pelo filtro da empresa atual; sem empresa, não aparece nada."""

    def get_queryset(self):
        company = get_current_company()
        queryset = super().get_queryset()
        if company is None:
            return queryset.none()
        return queryset.filter(company=company)
