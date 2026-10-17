# Noite do Código · Django REST framework

O sistema da **Noite do Código**: chamada de palestras de um meetup. O palestrante envia propostas para os eventos abertos,
anexa slides e acompanha as próprias palestras; visitantes se inscrevem para receber novidades.

Esta versão acrescenta uma **API REST com Django REST framework** ao app, com os mesmos endpoints e regras da
versão [`django-ninja`](../django-ninja/).

## O que tem aqui

- `Serializer` e `ModelSerializer`, validação com resposta **400**
- `ViewSet` + `DefaultRouter` e a API navegável do DRF
- Autenticação por chave (`X-API-Key`) e pela sessão
- Permissões de API, incluindo uma permissão por objeto (só o dono altera)
- Paginação, **django-filter** e throttling
- Testes com `APIClient`
- Documentação OpenAPI/Swagger com **drf-spectacular**

## Endpoints

| Método e URL | O que faz |
|---|---|
| `GET /api/` | raiz da API navegável |
| `GET /api/events/` | eventos |
| `GET /api/talks/` · `GET /api/talks/<id>/` | palestras |
| `POST /api/talks/` | cria (chave de API) |
| `PATCH /api/talks/<id>/` | altera (só o dono) |
| `GET /api/me/` | quem está logado |
| `GET /api/stats/` | com throttling |
| `/api/docs/` | Swagger · `/api/schema/` o OpenAPI |

## Experimente

```bash
curl -s http://127.0.0.1:8000/api/talks/
curl -s -X POST http://127.0.0.1:8000/api/talks/ -H "X-API-Key: ndc-regis-7f3a9c" \
     -H "Content-Type: application/json" -d @talk.json
```

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd django-rest-framework
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000. Usuários de exemplo, todos com a senha **`noite-do-codigo`**: `regis` e `bruno` (palestrantes). Para o admin, crie um superusuário com `uv run python manage.py createsuperuser`.

Testes: `uv run python manage.py test` (24 testes).

O banco é SQLite para rodar sem instalar nada; num projeto de verdade, prefira PostgreSQL ([por quê](https://youtube.com/shorts/ikCqYsBHr6k)).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
