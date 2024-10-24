from django.core.management.base import BaseCommand
from pandas import read_xml
from accounting.models.currencyCBR import CurrencyCBR


class Command(BaseCommand):
    help = 'Создает валюты (наименование, цифровой код, символьный код) на основе данных от ЦБ РФ'

    def handle(self, *args, **options):

        currencies = CurrencyCBR.objects.all().values_list('num_code', flat=True)
        if 643 not in currencies:
            CurrencyCBR.objects.create(num_code=643, char_code='RUB', name='Российский рубль')

        df = read_xml('https://www.cbr-xml-daily.ru/daily_utf8.xml')
        create_list = []
        for row in df.iterrows():

            currencyData = {
                    'num_code': row[1]['NumCode'],
                    'char_code': row[1]['CharCode'],
                    'name': row[1]['Name'],
            }

            if currencyData['num_code'] not in currencies:
                create_list.append(CurrencyCBR(**currencyData))

        CurrencyCBR.objects.bulk_create(create_list)
