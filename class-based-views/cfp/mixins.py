class OwnerQuerysetMixin:
    """Só os objetos de quem está logado: serve para lista, detalhe, edição e exclusão."""

    def get_queryset(self):
        return super().get_queryset().filter(submitted_by=self.request.user)


class UserFormKwargsMixin:
    """Entrega o usuário logado para o form (o TalkForm recebe user=...)."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
