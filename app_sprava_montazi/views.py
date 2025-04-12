"""app_sprava_montazi View"""

from time import sleep
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView, View


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "base.html"


class HomePageView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        template_name = "app_sprava_montazi/homepage.html"
        sleep(2)
        return render(self.request, template_name)


class DashboardView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        template_name = "app_sprava_montazi/dashboard.html"
        sleep(2)
        return render(self.request, template_name)
