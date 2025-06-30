from django.shortcuts import render


def index(request):
    return render(request, "form_builder/index.html")
