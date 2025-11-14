import os
import json
from django.core.management.base import BaseCommand, CommandError
from wbhb.viewer.utilities import fill_caches


class Command(BaseCommand):

    def handle(self, *args, **options):
        fill_caches()
