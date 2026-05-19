import logging

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import Guy
from .services import RandomGuysAPIError, load_guys

logger = logging.getLogger(__name__)


def index(request):
    """Главная страница, с таблицей с пагинацией и опцией загрузки новых записей"""
    queryset = Guy.objects.all().order_by('id')
    paginator = Paginator(queryset, settings.PEOPLE_PER_PAGE)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    return render(request, 'guys/index.html', {
        'page_obj': page_obj,
        'total_count': paginator.count,
    })


@require_http_methods(['POST'])
def load(request):
    """Загрузить еще N человек из внешнего API"""
    try:
        count = int(request.POST.get('count', '0'))
    except (TypeError, ValueError):
        count = 0

    if count <= 0:
        messages.error(request, 'Введите положительное число.')
        return HttpResponseRedirect(reverse('guys:index'))
    if count > 5000:
        messages.error(request, 'За один раз можно загрузить максимум 5000.')
        return HttpResponseRedirect(reverse('guys:index'))

    try:
        created = load_guys(count)
        messages.success(request, f'Успешно загружено: {created}')
    except RandomGuysAPIError as exc:
        logger.exception('Failed to load guys from API')
        messages.error(request, f'Ошибка обращения к API: {exc}')

    return HttpResponseRedirect(reverse('guys:index'))


def detail(request, user_id: int):
    """Детальная информация о конкретном человекеЫ"""
    guy = get_object_or_404(Guy, pk=user_id)
    return render(request, 'guys/detail.html', {'guy': guy})


@never_cache
def random_guy(request):
    """Получаем случайного человека; обновление страницы выдает другого человека"""
    guy = Guy.objects.order_by('?').first()
    if guy is None:
        return render(request, 'guys/empty.html', status=404)
    return render(request, 'guys/detail.html', {'guy': guy, 'is_random': True})
