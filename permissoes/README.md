# Noite do Código · Permissões no Django

O sistema da **Noite do Código**: chamada de palestras de um meetup. O palestrante envia propostas para os eventos abertos,
anexa slides e acompanha as próprias palestras; visitantes se inscrevem para receber novidades.

Esta versão responde **quem pode fazer o quê**: palestrante edita só a própria palestra, organizador aprova
as palestras do evento dele e o admin vê tudo.

## O que tem aqui

- As 4 permissões automáticas (`add`, `change`, `delete`, `view`) e a permissão própria `approve_talk` no `Meta`
- O grupo **Organizers**
- Views protegidas com função (`@login_required`, `@permission_required(..., raise_exception=True)`) e com classe
  (`PermissionRequiredMixin`, `UserPassesTestMixin`)
- `{{ perms }}` no template para mostrar ou esconder botões
- Permissão por objeto: um backend próprio (`cfp/backends.py`) e regras com **django-rules** (`cfp/rules.py`)
- Página 403 com o visual do site
- Testes de permissão

## Experimente

1. Entre como `regis`: veja e edite só as suas palestras.
2. Entre como `bruno`: em `/review/`, aprove palestras do evento #12; o #13 não é dele e dá 403.
3. Entre como `admin`: o superusuário passa em tudo.

## Páginas

| URL | O que é |
|---|---|
| `/talks/` | minhas palestras |
| `/talks/<id>/edit/` | edição (só o dono) |
| `/review/` | fila de aprovação (grupo Organizers) |
| `/talks/<id>/approve/` | aprovar (organizador do evento) |
| `/organizer/` | painel do organizador |
| `/admin/` | admin |

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd permissoes
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000. Usuários de exemplo, todos com a senha **`noite-do-codigo`**: `regis` (palestrante), `bruno` (palestrante e organizador do evento #12, grupo **Organizers**), `caio` (staff) e `admin` (superusuário).

Testes: `uv run python manage.py test` (7 testes).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
