import logging

from django.core.management.base import BaseCommand

from recipes.models import Tag

logger = logging.getLogger(__name__)

tags = [
    {
        'name': 'Завтак',
        'color': '#E26C2D',
        'slug': 'breakfast'
    },
    {
        'name': 'Обед',
        'color': '#49B64E',
        'slug': 'lunch'
    },
    {
        'name': 'ужин',
        'color': '#8775D2',
        'slug': 'dinner'
    }
]


class Command(BaseCommand):
    help = 'Import tags to database.'

    def handle(self, **kwargs):
        for data in tags:
            Tag.objects.get_or_create(
                name=data['name'],
                color=data['color'],
                slug=data['slug']
            )
            logger.info(f'Запись сохранена: {data}')
