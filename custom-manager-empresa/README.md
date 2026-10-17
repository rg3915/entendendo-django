# Vendas de 3 empresas · separando os dados com Custom Manager

Um sistema de vendas usado por **três empresas no mesmo banco**: Café Aroma, Pão da Vila e Doce Lar. Cada empresa tem seus
produtos, clientes e vendas, e nenhuma pode ver os dados da outra. A separação é feita **sem multi-tenant por schema**: uma
`ForeignKey` para `Company` em cada tabela e um **Custom Manager** que filtra tudo pela empresa do usuário logado.

## O que tem aqui

- `core/tenancy.py`: a empresa da requisição num `ContextVar` (funciona em views síncronas e async) e o `company_scope()` para shell e scripts
- `core/middleware.py`: define a empresa a partir de `request.user.company` (depois do `AuthenticationMiddleware`)
- `core/managers.py`: `CompanyManager` filtrando pela empresa (sem empresa → `none()`) e `all_objects` explícito para ver tudo
- `core/models.py`: `save()` preenche a empresa, `check_same_company()` impede FK apontando para outra empresa,
  `UniqueConstraint(company, email)`
- `core/forms.py`: querysets do `<select>` montados no `__init__`, a cada requisição
- `core/admin.py`: superusuário vê todas as empresas
- `core/views.py`: cache com a empresa na chave
- `core/tests.py`: **testes de isolamento** (a empresa A nunca vê a B)

Pegadinhas que o projeto cobre: thread-local que gruda na thread, `<select>` montado no import (uma empresa vê os produtos de
outra), FK que vaza pelo `_base_manager`, `bulk_create` que não chama `save()`, unique no banco inteiro, admin/`raw()`/`dumpdata`,
cache com chave fixa, consultas que começam em modelos sem empresa (`User`, `Company`).

Quando isso não basta: Row Level Security do Postgres ou um schema por empresa.

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd custom-manager-empresa
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000 e entre com um usuário de cada empresa, todos com a senha **`demo12345`**:

| Usuário | Empresa |
|---|---|
| `regis` | Café Aroma |
| `bruno` | Pão da Vila |
| `carla` | Doce Lar |

Para o admin com todas as empresas: `uv run python manage.py createsuperuser`.

| URL | O que é |
|---|---|
| `/` | produtos da sua empresa |
| `/itens/novo/` | novo item de venda (o `<select>` só mostra os produtos da sua empresa) |
| `/painel/` | total vendido (com cache por empresa) |
| `/async/produtos/` | a mesma lista numa view async |
| `/admin/` | admin |

Para testar com servidor ASGI: `uv run uvicorn config.asgi:application`.

Testes: `uv run python manage.py test` (11 testes).

O banco é SQLite para rodar sem instalar nada; num projeto de verdade, prefira PostgreSQL
([por quê](https://youtube.com/shorts/ikCqYsBHr6k)).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
