from django.views.generic import TemplateView


class WelcomeView(TemplateView):
    template_name = 'welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
