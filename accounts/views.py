"""Account views"""

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"Uzivatel {user} vytvořen.")
        login(self.request, user)
        return super().form_valid(form)
