# Noite do Código · Class-Based Views

O sistema da **Noite do Código**: chamada de palestras de um meetup. O palestrante envia propostas para os eventos abertos,
anexa slides e acompanha as próprias palestras; visitantes se inscrevem para receber novidades.

Esta versão reescreve o app com **Class-Based Views**, mantendo algumas views de função para comparar.

## O que tem aqui

- `View` e `as_view()`/`dispatch()` (`/ping/`)
- `TemplateView`, `RedirectView` (inclusive o `preserve_request` do Django 6.1)
- `ListView` com paginação e `DetailView`
- `CreateView`, `UpdateView` e `DeleteView`, com `get_form_kwargs` e `form_valid`
- Mixins: `LoginRequiredMixin` e dois mixins próprios (`cfp/mixins.py`)
- Um **rastreador** (`cfp/trace.py`) que imprime no terminal cada método da CBV na ordem em que o Django chama

## Páginas

| URL | O que é |
|---|---|
| `/` | início (`TemplateView`) |
| `/ping/` | a CBV mínima |
| `/subscribe/` · `/subscribe-fbv/` | inscrição com `FormView` e com função |
| `/talks/` · `/talks-fbv/` | minhas palestras com `ListView` e com função |
| `/talks/new/` | `CreateView` · `/talks/new-traced/` a mesma com o rastreador ligado (veja o terminal) |
| `/talks/<id>/`, `/edit/`, `/delete/` | `DetailView`, `UpdateView`, `DeleteView` |
| `/proposals/` e `/submit/` | `RedirectView` para as URLs novas |

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd class-based-views
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000. Usuários de exemplo, todos com a senha **`noite-do-codigo`**: `regis` e `bruno` (palestrantes). Para o admin, crie um superusuário com `uv run python manage.py createsuperuser`.

Testes: `uv run python manage.py test` (15 testes).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
