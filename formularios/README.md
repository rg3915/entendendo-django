# Noite do Código · Formulários do Django

O sistema da **Noite do Código**: chamada de palestras de um meetup. O palestrante envia propostas para os eventos abertos,
anexa slides e acompanha as próprias palestras; visitantes se inscrevem para receber novidades.

Esta versão destaca o **sistema de formulários do Django**.

## O que tem aqui

- `Form` e `ModelForm`, e o HTML que o `{{ form }}`, `as_p`, `as_div` e `as_field_group` geram
- O ciclo GET × POST na mesma view, formulário vinculado (bound) × não vinculado, redirect depois do POST
- Validators, `clean_<campo>()` e `clean()`, mensagens de erro e acessibilidade (`aria-invalid`, `aria-describedby`)
- Widgets, incluindo os novos `TelInput`, `ColorInput` e `SearchInput`
- ModelForm com ForeignKey e ManyToMany, `save(commit=False)` e `save_m2m()`
- Passar o usuário logado para o formulário
- Upload de um arquivo e de vários arquivos
- Formsets, `inlineformset_factory` e o `management_form`
- Validação ao vivo do título com **htmx** e debounce
- O mesmo formulário com **crispy-tailwind** e **django-widget-tweaks** (páginas com Tailwind)

O resto do site usa **Pico CSS** sem nenhuma classe no HTML.

## Páginas

| URL | O que é |
|---|---|
| `/` | início, com os eventos |
| `/subscribe/` | inscrição para receber novidades |
| `/guests/` | formset: vários convidados de uma vez |
| `/talks/` | minhas palestras (login) |
| `/talks/new/` | enviar palestra (CBV) · `/talks/new-fbv/` a mesma com função |
| `/talks/<id>/` e `/talks/<id>/edit/` | detalhe e edição, com anexos (inline formset) |
| `/tw/crispy/`, `/tw/helper/`, `/tw/tweaks/` | o mesmo form com crispy-tailwind, FormHelper e widget-tweaks |
| `/admin/` | admin do Django |

## Como rodar

Pré-requisito: [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.14 se precisar). Veja o [README principal](../README.md).

```bash
cd formularios
uv sync
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Abra http://127.0.0.1:8000. Usuários de exemplo, todos com a senha **`noite-do-codigo`**: `regis` e `bruno` (palestrantes). Para o admin, crie um superusuário com `uv run python manage.py createsuperuser`.

Testes: `uv run python manage.py test` (15 testes).

Projeto de estudo: a `SECRET_KEY`, o `DEBUG=True` e as senhas do seed são de demonstração.

Faz parte da série [Entendendo o Django](../README.md) do canal [Regis do Python](https://www.youtube.com/@RegisdoPython).
