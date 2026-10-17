# Entendendo o Django — Noite do Código

A **Noite do Código** é um sistema de **chamada de palestras (call for papers)** para um meetup de programação, feito em Django.
O palestrante entra, envia propostas para os próximos eventos, anexa slides e acompanha o que mandou. O organizador revisa e aprova
as palestras do evento dele. Os visitantes se inscrevem para receber novidades, e há uma API REST para integrar com outros sistemas.

O mesmo sistema aparece em seis versões. Cada uma destaca uma parte do Django e funciona sozinha, como um projeto completo:

| Pasta | O que essa versão mostra |
|---|---|
| [`formularios/`](formularios/) | Forms e ModelForms: `as_p`/`as_div`, GET × POST, validação, widgets, upload simples e múltiplo, formsets, validação ao vivo com htmx, crispy-tailwind e widget-tweaks |
| [`class-based-views/`](class-based-views/) | O mesmo app com Class-Based Views: `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `RedirectView`, mixins próprios e um rastreador que mostra a ordem dos métodos |
| [`permissoes/`](permissoes/) | Quem pode fazer o quê: permissões e grupos, views protegidas, `{{ perms }}` no template, permissão por objeto com backend próprio e com django-rules |
| [`django-ninja/`](django-ninja/) | API REST com Django Ninja: schemas, routers, chave de API, sessão, paginação, filtros, PATCH, async, throttling e Swagger |
| [`django-rest-framework/`](django-rest-framework/) | A mesma API com Django REST framework: serializers, ViewSets, router, permissões, django-filter e drf-spectacular |
| [`drf-vs-ninja/`](drf-vs-ninja/) | As duas APIs no mesmo projeto, lado a lado, com testes das duas e um benchmark |

Os vídeos de cada versão estão no canal [Regis do Python](https://www.youtube.com/@RegisdoPython) (série "Entendendo o Django"),
mas você não precisa deles para rodar nem para estudar o código.

## Tecnologias

- Python 3.14 e Django 6.1
- SQLite (nenhum banco para instalar), para você rodar em segundos
- [Pico CSS](https://picocss.com/) sem classes no HTML e [htmx](https://htmx.org/) por CDN
- [uv](https://docs.astral.sh/uv/) para dependências e ambiente virtual

## Como rodar na sua máquina

### 1. Pré-requisitos

Você só precisa do **uv**. Ele baixa o Python 3.14 sozinho se você não tiver.

```bash
# Linux e macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Baixe o código

```bash
git clone https://github.com/rg3915/entendendo-django.git
cd entendendo-django
```

### 3. Escolha uma versão e rode

Cada pasta é um projeto independente. Entre na que quiser (aqui, `formularios`):

```bash
cd formularios
uv sync                                  # cria o .venv e instala as dependências
uv run python manage.py migrate          # cria o banco SQLite
uv run python manage.py seed             # eventos, tags, palestras e usuários de exemplo
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000 e entre com um dos usuários abaixo.

### 4. Usuários de exemplo

Todos com a senha **`noite-do-codigo`**:

| Usuário | Papel |
|---|---|
| `regis` | palestrante |
| `bruno` | palestrante (na versão `permissoes/`, organizador do evento #12) |
| `caio` | staff (só na versão `permissoes/`) |
| `admin` | superusuário (só na versão `permissoes/`; nas outras, crie com `uv run python manage.py createsuperuser`) |

Nas versões com API, o seed também cria as chaves `ndc-regis-7f3a9c` e `ndc-bruno-2b8e41`, enviadas no cabeçalho `X-API-Key`.

### 5. Rode os testes

```bash
uv run python manage.py test
```

## Estrutura de cada versão

```
<pasta>/
├── config/          # settings, urls, asgi/wsgi
├── cfp/             # o app: models, forms, views, templates, testes
│   └── management/commands/seed.py
├── manage.py
├── pyproject.toml   # dependências
└── uv.lock          # versões exatas
```

## E o banco de dados?

Os exemplos usam **SQLite** só para você clonar e rodar sem instalar nada. Para um projeto de verdade, eu sugiro usar
**PostgreSQL** desde o começo: o SQLite aceita coisas que o Postgres recusa e pode esconder bugs que só aparecem em produção.
Falo sobre isso neste vídeo: [O SQLite está escondendo um bug de você](https://youtube.com/shorts/ikCqYsBHr6k).

Para trocar, instale o driver (`uv add "psycopg[binary]"`) e mude o `DATABASES` no `config/settings.py`.

## Avisos

- É um projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração. Não use assim em produção.
- Para recomeçar do zero, apague o `db.sqlite3` e rode `migrate` e `seed` de novo.
