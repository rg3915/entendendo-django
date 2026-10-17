# Noite do Código · Django Ninja

O sistema da **Noite do Código**: chamada de palestras de um meetup. O palestrante envia propostas para os eventos abertos,
anexa slides e acompanha as próprias palestras; visitantes se inscrevem para receber novidades.

Esta versão acrescenta uma **API REST com Django Ninja** ao app.

## O que tem aqui

- `Schema` e `ModelSchema` (Pydantic), validação com resposta **422**
- Routers e a classe `Status` para códigos HTTP
- Autenticação por chave (`X-API-Key`) e pela sessão do Django
- Paginação, `FilterSchema`, PATCH parcial com `PatchDict`
- Endpoint async e throttling (3 pedidos a cada 10 s)
- Testes com `TestClient`
- Documentação **Swagger** gerada sozinha

## Endpoints

| Método e URL | O que faz |
|---|---|
| `GET /api/events/` | eventos |
| `GET /api/talks/` | palestras (paginação e filtros) |
| `GET /api/talks/<id>` | uma palestra |
| `POST /api/talks/` | cria (chave de API) |
| `PATCH /api/talks/<id>` | altera só os campos enviados (só o dono) |
| `GET /api/me` | quem está logado (sessão) |
| `GET /api/stats` | async, com throttling |
| `/api/docs` | Swagger |

## Experimente

```bash
curl -s http://127.0.0.1:8000/api/talks/
curl -s -X POST http://127.0.0.1:8000/api/talks/ -H "X-API-Key: ndc-regis-7f3a9c" \
     -H "Content-Type: application/json" -d @talk.json
```

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd django-ninja
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000. Usuários de exemplo, todos com a senha **`noite-do-codigo`**: `regis` e `bruno` (palestrantes). Para o admin, crie um superusuário com `uv run python manage.py createsuperuser`.

Testes: `uv run python manage.py test` (23 testes).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
