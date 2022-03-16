import re
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from wbhb.viewer.models import *

'''
publishers = Publisher.objects()
for publisher in publishers:
    publisher.delete()
    
languages = Language.objects()
for language in languages:
    language.delete()
    
genres = Genre.objects()
for genre in genres:
    genre.delete()
    
formats = Format.objects()
for format in formats:
    format.delete()
    
roles = Role.objects()
for role in roles:
    role.delete()
'''


def escape(val):
    if val:
        return val.replace("'", "\\'")
    return ''

class Command(BaseCommand):

    def handle(self, *args, **options):

        with open(settings.BASE_DIR + '/load_collex_data.py', 'w') as migrate:
            migrate.write('''
import re
from cms.custom_types import *
from bson import ObjectId
            ''')

            # PUBLISHERS
            migrate.write('''
publisher_map = {}
            ''')
            publishers = Publisher.objects.filter()
            for publisher in publishers:
                migrate.write('''
p = Publisher()
p.press = '{press}'
p.save()
publisher_map['{id}'] = p.id
                '''.format(
                    press=escape(publisher.press),
                    id=publisher.id
                ))

            # LANGUAGES
            migrate.write('''
language_map = {}
            ''')
            languages = Language.objects.filter()
            for language in languages:
                migrate.write('''
l = Language()
l.name = '{name}'
l.save()
language_map['{id}'] = l.id
                '''.format(
                    name=escape(language.name),
                    id=language.id
                ))

            # GENRES
            migrate.write('''
genre_map = {}
            ''')
            genres = Field.objects.filter()
            for genre in genres:
                migrate.write('''
g = Genre()
g.name = '{name}'
g.save()
genre_map['{id}'] = g.id
                '''.format(
                    name=escape(genre.name),
                    id=genre.id
                ))

            # FORMATS
            migrate.write('''
format_map = {}
            ''')
            formats = Format.objects.filter()
            for format in formats:
                migrate.write('''
f = Format()
f.type = '{type}'
f.save()
format_map['{id}'] = f.id
                    '''.format(
                    type=escape(format.type),
                    id=format.id
                ))

            # ROLES
            migrate.write('''
role_map = {}
                ''')
            roles = Role.objects.filter()
            for role in roles:
                migrate.write('''
r = Role()
r.function = '{function}'
r.save()
role_map['{id}'] = r.id
                        '''.format(
                    function=escape(role.function),
                    id=role.id
                ))

            # PEOPLE
            migrate.write('''
person_map = {}
                    ''')
            people = Person.objects.filter()
            for person in people:
                migrate.write('''
p = Person()
p.first_name = '{first_name}'
p.last_name = '{last_name}'
p.title = '{title}'
p.save()
person_map['{id}'] = p.id
                            '''.format(
                    first_name=escape(person.first_name),
                    last_name=escape(person.last_name),
                    title=escape(person.title),
                    id=person.id
                ))

            # RolePeople
            role_people = RolePerson.objects.filter()
            migrate.write('''
rolepersons_to_entries = {}
            ''')
            for role_person in role_people:
                migrate.write('''
try:
    rp = RolePerson.objects(role=ObjectId(role_map['{role_id}']), person=ObjectId(person_map['{person_id}']))[0]
except:
    rp = RolePerson()
    rp.role = ObjectId(role_map['{role_id}'])
    rp.person = ObjectId(person_map['{person_id}'])
    rp.save()

if rp.id not in rolepersons_to_entries:
    rolepersons_to_entries[rp.id] = []

rolepersons_to_entries[rp.id].append('{entry_id}')
                '''.format(
                    role_id=role_person.role.id,
                    person_id=role_person.person.id,
                    entry_id=role_person.source.id
                ))

            # Cities
            cities = Location.objects.filter()
            migrate.write('''
city_map = {}
            ''')
            for city in cities:
                migrate.write('''
c = City()
c.name = '{name}'
c.save()
city_map['{id}'] = c.id
                '''.format(
                    name=escape(city.country),
                    id=city.id
                ))

            # Entries
            entries = Source.objects.filter()
            migrate.write('''
entry_map = {}
relationships = []
            ''')
            for entry in entries:
                migrate.write('''
e = BibliographicEntry()
e.title = '{title}'
e.contained_in = '{contained_in}'
e.serial_title = '{serial_title}'
e.location_details = '{location_details}'
e.notes = ''\'{private_notes}''\'
e.descriptive_notes = ''\'{descriptive_notes}''\'
e.scholarship_notes = ''\'{scholarship_notes}''\'
e.prior_doc_notes = ''\'{prior_doc_notes}''\'
e.authentication_notes = ''\'{authentication_notes}''\'

publisher_id = '{publisher_id}'
if publisher_id != 'None':
    e.publisher = ObjectId(publisher_map[publisher_id])
    
e.identifying_numbers = '{doi}'

language_id = '{language_id}'
if language_id != 'None':
    e.languages.append(ObjectId(language_map['{language_id}']))
    
for rp_id in rolepersons_to_entries.keys():
    if '{id}' in rolepersons_to_entries[rp_id]:
        e.roles.append(ObjectId(rp_id))
                '''.format(
                    title=escape(entry.title),
                    contained_in=escape(entry.container),
                    serial_title=escape(entry.series_title),
                    location_details=escape(entry.pages),
                    private_notes=escape(entry.institution),
                    descriptive_notes=escape(entry.notes),
                    scholarship_notes=escape(entry.notes2),
                    prior_doc_notes=escape(entry.notes3),
                    authentication_notes=escape(entry.notes4),
                    publisher_id=entry.publisher.id if entry.publisher else None,
                    doi=escape(entry.doi),
                    language_id=entry.language.id if entry.language else None,
                    id=entry.id
                ))

                # convert date string to number
                migrate.write('''
date_string = '{pub_year}'
pattern = re.compile(r'(\d\d\d\d)')
matches = pattern.findall(date_string)
if matches:
    e.date = int(matches[0])
                '''.format(
                    pub_year=entry.pub_year
                ))

                # cities
                for location in entry.locations.all():
                    migrate.write('''
e.cities.append(ObjectId(city_map['{location_id}']))
                    '''.format(
                        location_id=location.id
                    ))

                # genres
                for genre in entry.fields.all():
                    migrate.write('''
e.genres.append(ObjectId(genre_map['{genre_id}']))
                        '''.format(
                        genre_id=genre.id
                    ))

                # formats
                for format in entry.formats.all():
                    migrate.write('''
e.formats.append(ObjectId(format_map['{format_id}']))
                            '''.format(
                        format_id=format.id
                    ))

                migrate.write('''
e.save()
entry_map[{0}] = str(e.id)
                '''.format(entry.id))

                # relationships
                entry_relations = RelationSource.objects.filter(from_source=entry).order_by('relationship')
                for entry_relation in entry_relations:
                    migrate.write('''
relationships.append({{
    'source': {0},
    'target': {1},
    'relation': '{2}'
}})
                    '''.format(
                        entry.id,
                        entry_relation.to_source.id,
                        escape(entry_relation.relationship.relationship)
                    ))

            # RELATIONSHIPS
            migrate.write('''
relation_up_down = {
    "(Upstream) Expands upon": "(Downstream) Expanded in",
    "(Upstream) Extracts from": "(Downstream) Excerpted as",
    "(Upstream) Incorporates": "(Downstream) Incorporated in",
    "(Upstream) Is a markup and performance of": "(Downstream) Marked up and performed as",
    "(Upstream) Is a performance of": "(Downstream) Performed as",
    "(Upstream) Reformats": "(Downstream) Reformatted as",
    "(Upstream) Reformats and recontextualizes": "(Downstream) Reformatted and recontextualized as",
    "(Upstream) Relies on": "(Downstream) Is relied on by",
    "(Upstream) Reproduces in new context": "(Downstream) Reproduced in new context as",
    "(Upstream) Reproduces with new title": "(Downstream) Reproduced with new title as",
    "(Upstream) Responds to": "(Downstream) Responded to in",
    "(Upstream) Reuses art from": "(Downstream) Art is reused in",
    "(Upstream) Reuses text from": "(Downstream) Text is reused in",
    "(Upstream) Revises": "(Downstream) Revised as",
    "(Upstream) Revises and incorporates": "(Downstream) Revised and incorporated in",
    "(Upstream) Revises and recontextualizes": "(Downstream) Revised and recontextualized as",
    "(Upstream) Translates": "(Downstream) Translated as",
    "(Upstream) Uses excerpts from": "(Downstream) Excerpts used in",
    "Also published as": "Also published as",
    "Collocates with": "Collocates with",
    "Forms series with": "Forms series with",
    "See also": "See also"
}

for upstream in relation_up_down.keys():
    rt = RelationshipType()
    rt.source_to_target = upstream
    rt.target_to_source = relation_up_down[upstream]
    rt.save()
    relation_up_down[upstream] = {
        "downstream": rt.target_to_source,
        "id": str(rt.id)
    }

saved_relationships = []

for relationship in relationships:
    if relationship['relation'] in relation_up_down:
        relation_key = "{0}|{1}|{2}".format(
            relationship['source'],
            relationship['relation'],
            relationship['target']
        )
        if relation_key not in saved_relationships:
            reverse_relation_key = "{0}|{1}|{2}".format(
                relationship['target'],
                relation_up_down[relationship['relation']]['downstream'],
                relationship['source']
            )
        
            bib_rel = BibliographicRelationship()
            bib_rel.source_entry = ObjectId(entry_map[relationship['source']])
            bib_rel.target_entry = ObjectId(entry_map[relationship['target']])
            bib_rel.relationship_type = ObjectId(relation_up_down[relationship['relation']]['id'])
            bib_rel.save()
            saved_relationships.append(reverse_relation_key)
            ''')

