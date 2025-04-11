"""app_sprava_montazi View"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "base.html"


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "app_sprava_montazi/homepage.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "app_sprava_montazi/dashboard.html"
