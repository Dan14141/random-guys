from django.shortcuts import render
from .models import Guy


def index(request):
    guys = Guy.objects.all().order_by('id')
    return render(request, 'guys/index.html', {'guys': guys})