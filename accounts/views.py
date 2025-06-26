"""Account views"""

import logging
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages

# ---
logger_login = logging.getLogger("login")


class CustomLoginView(LoginView):
    def form_invalid(self, form):
        username = self.request.POST.get("username", "neznámý uživatel")
        logger_login.warning(
            "login failed: %s z IP: %s",
            username,
            self.get_client_ip(),
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        username = self.request.POST.get("username", "neznámý uživatel")
        logger_login.info(
            "login succeeded: %s z IP: %s",
            username,
            self.get_client_ip(),
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return self.request.META.get("REMOTE_ADDR")


class RegisterView(LoginRequiredMixin, FormView):
    template_name = "registration/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"Uzivatel {user} vytvořen.")
        login(self.request, user)
        return super().form_valid(form)
