import os
import json
from pathlib import Path
from django.template import loader, Context
from wbhb.viewer.models import *


def fill_caches():
    sources = Source.objects.all()
    sources_json = make_sources_dict(sources)

    with open('sources_datatables.json', 'w') as fout:
        json.dump(sources_json, fout)

    template = loader.get_template('export.txt')

    with open('export.txt', 'w') as fout:
        fout.write(template.render({'sources': sources}).replace('\n', '\r\n'))


def make_sources_dict(sources):
    sources_json = {
        'data': []
    }
    for source in sources:
        people = "<div class='truncate'>"
        for person in source.roleperson_set.all():
            people += person.person.__str__() + " (" + person.role.function + ")<br>"
        if len(people) > 2:
            people = people[:-2]
        people += "</div>"

        countries = ""
        for location in source.locations.all():
            countries += location.__str__() + ", "
        if len(countries) > 2:
            countries = countries[:-2]

        fields = ""
        genres = [str(g) for g in source.fields.all()]
        if source.primary_genre:
            genres.insert(0, str(source.primary_genre))
        if genres:
            fields = "<br>".join(genres)

        languages = ""
        langs = [str(l) for l in source.languages.all()]
        if source.primary_language:
            langs.insert(0, str(source.primary_language))
        if langs:
            languages = "<br>".join(langs)

        s_data = [
            str(source.id),
            people,
            "<a href='/detail?id=" + str(source.id) + "' target='_blank'>" + source.title + "</a>",
            source.pub_year,
            languages,
            countries,
            fields,
            source.notes,
            source.notes2,
            source.notes3
        ]
        sources_json['data'].append(s_data)

    return sources_json