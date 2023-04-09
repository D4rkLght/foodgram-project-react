import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DIR = Path(settings.BASE_DIR).resolve().joinpath('data')
FILE = DIR / 'ingredients.csv'


class Command(BaseCommand):
    help = 'Import ingredients to database.'

    def handle(self, **kwargs):
        with open(FILE, 'r', encoding='UTF-8') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                print(row)
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
