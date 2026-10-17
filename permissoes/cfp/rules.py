import rules


@rules.predicate
def is_event_organizer(user, talk):
    """A palestra é de um evento que este usuário organiza."""
    return talk is not None and talk.event.organizer_id == user.pk


rules.add_perm("cfp.view_talk", is_event_organizer)
rules.add_perm("cfp.approve_talk", rules.is_group_member("Organizers") & is_event_organizer)
