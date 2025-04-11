"""app_sprava_montazi View"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from time import sleep


class HomePageView(LoginRequiredMixin, TemplateView):
    sleep(2)
    template_name = "app_sprava_montazi/homepage.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    sleep(2)
    template_name = "app_sprava_montazi/dashboard.html"
