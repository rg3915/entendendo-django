TRACED = {
    "setup", "dispatch", "get", "post", "get_form", "get_form_class", "get_form_kwargs", "get_initial",
    "form_valid", "form_invalid", "get_context_data", "get_success_url", "render_to_response", "get_template_names",
}


class TraceMixin:
    """Só para estudo: imprime no terminal cada método da CBV no momento em que o Django chama."""

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if name not in TRACED or not callable(attr):
            return attr

        def chamado(*args, **kwargs):
            print(f"   → {name}()")
            return attr(*args, **kwargs)

        return chamado
