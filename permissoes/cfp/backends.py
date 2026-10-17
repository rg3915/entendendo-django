from django.contrib.auth.backends import BaseBackend

from .models import Talk


class TalkOwnerBackend(BaseBackend):
    """Permissão por objeto: quem enviou a palestra pode ver e editar a palestra dele."""

    def has_perm(self, user_obj, perm, obj=None):
        if not isinstance(obj, Talk) or not user_obj.is_active:
            return False
        return perm in {"cfp.view_talk", "cfp.change_talk"} and obj.submitted_by_id == user_obj.pk
