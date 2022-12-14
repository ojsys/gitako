from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import logout, authenticate, login
from django.conf import settings
from . import forms
# Create your views here.

def logout_user(request):
    logout(request)
    return redirect('login')


def signup_page(request):
    form = forms.SignUpForm()
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Login the user
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup.html', {'form': form})



class LoginPageView(View):
    template_name = 'authentication/login.html'
    form_class = forms.LoginForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, {'message': message, 'form': form})


    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                message = f'Hello {user.username}, You are logged in successfully.'
                return redirect('index')
        message = 'Login failed'    
        return render(request, 'authentication/login.html', {'form': form, 'message': message})