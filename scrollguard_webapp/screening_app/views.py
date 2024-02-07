from django.shortcuts import render

# Create your views here.
def homepage(request):
    return render(request, "screening_app/home.html", {"title": "Home"})

def login(request):
    return render(request, "screening_app/login.html", {"title": "Login"})

def demo(request):
    return render(request, "screening_app/demo.html", {"title": "Demo"})

def contact(request):
    return render(request, "screening_app/contact.html", {"title": "Contact"})

def screening(request):
    return render(request, "screening_app/screen.html", {"title": "Screen"})