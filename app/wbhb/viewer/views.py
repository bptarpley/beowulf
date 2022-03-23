import os
import re
import json
from django.shortcuts import render, HttpResponse
from django.db.models import prefetch_related_objects, Q
from django.utils.html import escape
from django.conf import settings
from django.template import loader, Context
from django.db import connection

from .models import *


def index(request):

    pages = HTMLBlock.objects.all()

    return render(
        request,
        'index.html',
        {
            'pages': pages
        }
    )


def page(request, nice_url):
    pages = HTMLBlock.objects.all()

    default_block = {
        'name': "Oops!",
        'content': '''
            This page does not exist!
        '''
    }

    try:
        block = HTMLBlock.objects.get(name=nice_url)
    except:
        block = default_block

    return render(
        request,
        'page.html',
        {
            'pages': pages,
            'html_block': block
        }
    )


def source_detail(request):
    pages = HTMLBlock.objects.all()
    source = None
    last_update = None
    relationships = []

    if request.method == 'GET':
        id = _clean(request, 'id')
        source = Source.objects.get(id=id)
        relationships = RelationSource.objects.filter(from_source=source).order_by('relationship')

        try:
            cursor = connection.cursor()
            cursor.execute('''SELECT id FROM django_content_type where app_label="viewer" and model="source"''')
            row = cursor.fetchall()
            source_ct_id = row[0][0]
            cursor.execute(
                '''SELECT max(action_time) from django_admin_log where content_type_id={0} and object_id={1}'''.format(
                    source_ct_id,
                    id
                )
            )
            row = cursor.fetchall()
            last_update = row[0][0].strftime("%m/%d/%Y")
        except:
            last_update = None

    return render(
        request,
        'source_detail.html',
        {
            'source': source,
            'relationships': relationships,
            'pages': pages,
            'last_update': last_update
        }
    )


def relationship_graph(request):
    graph = {
        'nodes': [],
        'edges': []
    }

    source_id = _clean(request, 'id')
    source = Source.objects.get(id=source_id)
    node_ids = {}
    edge_keys = {}
    build_graph(source, graph, node_ids, edge_keys, True)

    return HttpResponse(
        json.dumps(graph),
        content_type='application/json'
    )


def build_graph(source, graph, node_ids, edge_keys, root=False):
    level = re.search(r'\b\d{4}\b|$', source.pub_year).group()
    if not level or not level.isdigit():
        level = 2000
    else:
        level = int(level)

    node = {
        'id': str(source.id),
        'label': str(source),
        'level': level,
        'color': '#5F0000' if root else '#5d737e'
    }
    if root:
        node['color'] = '#5F0000'
    graph['nodes'].append(node)
    node_ids[str(source.id)] = True

    relationships = RelationSource.objects.filter(from_source=source).order_by('relationship')
    related_sources = []
    for relation in relationships:
        rel_label = str(relation.relationship).strip()
        if rel_label not in ['See also']:
            edge_key = "{0}__{1}".format(source.id, relation.to_source.id)
            if int(source.id) > int(relation.to_source.id):
                edge_key = "{0}__{1}".format(relation.to_source.id, source.id)

            if edge_key not in edge_keys:
                rel_edge = {
                    'from': str(source.id),
                    'to': str(relation.to_source.id),
                    'title': rel_label,
                }
                if rel_label in ['Forms series with', 'Collocates with', 'Also published as']:
                    rel_edge['dashes'] = True

                graph['edges'].append(rel_edge)
                edge_keys[edge_key] = True
                related_sources.append(relation.to_source)

    for related_source in related_sources:
        if str(related_source.id) not in node_ids:
            build_graph(related_source, graph, node_ids, edge_keys)


def export(request):
    sources = None
    ids = []

    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="export.txt"'

    if request.method == 'POST':
        ids = _clean(request, 'ids', '', 'POST')
        if ids:
            ids = ids.split(',')

    if ids:
        sources = Source.objects.filter(id__in=ids)
    else:
        if os.path.exists('export.txt'):
            with open('export.txt', 'r') as fin:
                response.write(fin.read())
            return response
        else:
            sources = Source.objects.all()

    template = loader.get_template('export.txt')
    response.write(template.render({'sources': sources}).replace('\n', '\r\n'))

    return response


def sources(request):
    format = 'default'
    filter_string = None
    sources_json = []
    sources = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')
        filter_string = _clean(request, 'filter')

    sources = Source.objects.filter()

    if filter_string:
        filters = filter_string.split(",")
        for f in filters:
            f_parts = f.split("_")
            if len(f_parts) == 2:
                filter_type = f_parts[0]
                filter_id = f_parts[1]

                if filter_type == "person":
                    sources = sources.filter(roleperson__person__id=filter_id).distinct()
                if filter_type == "role":
                    sources = sources.filter(roleperson__role__id=filter_id).distinct()
                elif filter_type == "location":
                    sources = sources.filter(locations__id=filter_id)
                elif filter_type == "language":
                    sources = sources.filter(Q(languages__id=filter_id) | Q(primary_language__id=filter_id))
                elif filter_type == "publisher":
                    sources = sources.filter(publisher__id=filter_id)
                elif filter_type == "field":
                    sources = sources.filter(Q(fields__id=filter_id) | Q(primary_genre__id=filter_id))

    if format == 'default':
        for source in sources:
            sources_json.append(source.to_dict())
    elif format == 'datatables':

        if not filter_string:
            if os.path.exists(settings.TABLE_CACHE_FILE):
                with open(settings.TABLE_CACHE_FILE, 'r') as fin:
                    sources_json = json.load(fin)

        if not sources_json:
            sources_json = make_sources_dict(sources)

    return HttpResponse(
        json.dumps(sources_json),
        content_type='application/json'
    )


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


def people(request):
    format = 'default'
    people_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    people = Person.objects.all()

    if format == 'default':
        for person in people:
            people_json.append(person.to_dict())

    elif format == 'datatables':
        people_json = { 'data': [] }
        for person in people:
            people_json['data'].append(
                [
                    "<a href='javascript: filter(\"person\", " + str(person.id) + ", \"" + person.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + person.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(people_json),
        content_type='application/json'
    )


def locations(request):
    format = 'default'
    loc_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    locs = Location.objects.all()

    if format == 'default':
        for loc in locs:
            loc_json.append(loc.to_dict())
    elif format == 'datatables':
        loc_json = { 'data': [] }
        for loc in locs:
            loc_json['data'].append(
                [
                    "<a href='javascript: filter(\"location\", " + str(loc.id) + ", \"" + loc.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + loc.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(loc_json),
        content_type='application/json'
    )


def languages(request):
    format = 'default'
    lang_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    langs = Language.objects.all()

    if format == 'default':
        for lang in langs:
            lang_json.append(lang.to_dict())
    elif format == 'datatables':
        lang_json = {'data': []}
        for lang in langs:
            lang_json['data'].append(
                [
                    "<a href='javascript: filter(\"language\", " + str(lang.id) + ", \"" + lang.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + lang.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(lang_json),
        content_type='application/json'
    )


def publishers(request):
    format = 'default'
    pub_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    pubs = Publisher.objects.all()
    
    if format == 'default':
        for pub in pubs:
            pub_json.append(pub.to_dict())
    elif format == 'datatables':
        pub_json = {'data': []}
        for pub in pubs:
            pub_json['data'].append(
                [
                    "<a href='javascript: filter(\"publisher\", " + str(pub.id) + ", \"" + pub.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + pub.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(pub_json),
        content_type='application/json'
    )


def roles(request):
    format = 'default'
    rl_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    rls = Role.objects.all()

    if format == 'default':
        for rl in rls:
            rl_json.append(rl.to_dict())
    elif format == 'datatables':
        rl_json = {'data': []}
        for rl in rls:
            rl_json['data'].append(
                [
                    "<a href='javascript: filter(\"role\", " + str(rl.id) + ", \"" + rl.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + rl.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(rl_json),
        content_type='application/json'
    )


def fields(request):
    format = 'default'
    field_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    fields = Field.objects.all()

    if format == 'default':
        for field in fields:
            field_json.append(field.to_dict())
    elif format == 'datatables':
        field_json = {'data': []}
        for field in fields:
            field_json['data'].append(
                [
                    "<a href='javascript: filter(\"field\", " + str(field.id) + ", \"" + field.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + field.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(field_json),
        content_type='application/json'
    )


def periods(request):
    format = 'default'
    period_json = []

    if request.method == 'GET':
        format = _clean(request, 'format', 'default')

    periods = Period.objects.all()

    if format == 'default':
        for period in periods:
           period_json.append(period.to_dict())
    elif format == 'datatables':
        period_json = {'data': []}
        for period in periods:
            period_json['data'].append(
                [
                    "<a href='javascript: filter(\"period\", " + str(period.id) + ", \"" + period.__str__().replace('"', '').replace("'", "&apos;") + "\");'>" + period.__str__() + "</a>"
                ]
            )

    return HttpResponse(
        json.dumps(period_json),
        content_type='application/json'
    )


def _clean(request, param, default='', method='GET'):
    clean_value = None

    if method == 'GET':
        clean_value = escape(request.GET.get(param, default))
    elif method == 'POST':
        clean_value = escape(request.POST.get(param, default))

    return clean_value