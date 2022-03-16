import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.template import loader, Context
from wbhb.viewer.models import *
from wbhb.viewer.views import make_sources_dict


class Command(BaseCommand):

    def handle(self, *args, **options):

        if os.path.exists('fields.json'):
            print('yup')
        else:
            print('nope')

        sources = Source.objects.all()

        sources_json = make_sources_dict(sources)

        with open('sources_datatables.json', 'w') as fout:
            json.dump(sources_json, fout)

        template = loader.get_template('export.txt')
        #context = Context({'sources': sources})

        with open('export.txt', 'w') as fout:
            fout.write(template.render({'sources': sources}).replace('\n', '\r\n'))
