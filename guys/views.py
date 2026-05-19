from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404,render
from django.views.decorators.cache import never_cache
from .models import Guy


def index(request):
    queryset = Guy.objects.all().order_by('id')
    paginator = Paginator(queryset, 50)   # 50 на страницу
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    return render(request, 'guys/index.html', {'page_obj': page_obj})

def detail(request, user_id: int):
    guy = get_object_or_404(Guy, pk=user_id)
    return render(request, 'guys/detail.html', {'guy': guy})

@never_cache
def random_guy(request):
    guy = Guy.objects.order_by('?').first()
    if guy is None:
        return render(request, 'guys/empty.html', status=404)
    return render(request, 'guys/detail.html', {'guy': guy, 'is_random': True})