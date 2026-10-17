# Noite do Código · DRF ou Django Ninja?

O sistema da **Noite do Código**: chamada de palestras de um meetup. O palestrante envia propostas para os eventos abertos,
anexa slides e acompanha as próprias palestras; visitantes se inscrevem para receber novidades.

Esta versão tem **as duas APIs no mesmo projeto**, com o mesmo banco e as mesmas regras, para comparar
Django REST framework e Django Ninja lado a lado.

## O que tem aqui

- `cfp/api_ninja.py` e `cfp/api_drf.py` (+ `serializers.py` e `schema.py`): a mesma API escrita nos dois
- Testes das duas (`test_api_ninja.py` e `test_api_drf.py`), que garantem que elas se comportam igual
- Throttling de cada uma com chave de cache própria (as duas usavam a mesma por padrão)

## Endpoints

| Ninja | DRF |
|---|---|
| `/ninja/talks/` | `/drf/talks/` |
| `/ninja/events/` | `/drf/events/` |
| `/ninja/me` | `/drf/me/` |
| `/ninja/stats` | `/drf/stats/` |
| `/ninja/docs` | `/drf/docs/` |

## Experimente

```bash
curl -s -X POST http://127.0.0.1:8000/ninja/talks/ -H "X-API-Key: ndc-regis-7f3a9c" \
     -H "Content-Type: application/json" -d @talk_ninja.json
curl -s -X POST http://127.0.0.1:8000/drf/talks/ -H "X-API-Key: ndc-regis-7f3a9c" \
     -H "Content-Type: application/json" -d @talk_drf.json
```

Repare: o campo das tags se chama `tags` no Ninja e `tag_ids` no DRF.

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd drf-vs-ninja
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000. Usuários de exemplo, todos com a senha **`noite-do-codigo`**: `regis` e `bruno` (palestrantes). Para o admin, crie um superusuário com `uv run python manage.py createsuperuser`.

Testes: `uv run python manage.py test` (32 testes).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
