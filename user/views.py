from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_user(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('mpc:dashboard')
        else:
            messages.error(request, 'Login inválido! Por favor, tente novamente.')
            return redirect('user:login')

    else:
        return render(request, 'authenticate/login.html', {})


def logout_user(request):  
    logout(request)
    messages.success(request, 'Usuário deslogado com sucesso')
    return redirect('user:login')



