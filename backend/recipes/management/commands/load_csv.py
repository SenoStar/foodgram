import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Импортирует данные из CSV файлов'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            ingredients = []
            for string in reader:
                name, measurement_unit = string
                if name:
                    ingredient = Ingredient(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    ingredients.append(ingredient)
            Ingredient.objects.bulk_create(ingredients)
