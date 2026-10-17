"""A empresa da requisição atual, guardada num ContextVar (vale para sync e async, e some no fim)."""
from contextlib import contextmanager
from contextvars import ContextVar

_company = ContextVar("company", default=None)


def get_current_company():
    """Devolve a empresa do contexto atual, ou None."""
    return _company.get()


@contextmanager
def company_scope(company):
    """Define a empresa dentro do bloco e devolve a anterior na saída (requisição, shell, tarefa, teste)."""
    token = _company.set(company)
    try:
        yield company
    finally:
        _company.reset(token)
