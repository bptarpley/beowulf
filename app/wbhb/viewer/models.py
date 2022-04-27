from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache


class Publisher(models.Model):
    press = models.CharField(max_length=200)

    def __str__(self):
        return self.press

    def to_dict(self):
        return {
            'id': self.id,
            'press': self.press
        }

    class Meta:
        ordering = ['press']


class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    class Meta:
        ordering = ['name']


# GENRES
class Field(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        ordering = ['name']


class Format(models.Model):
    type = models.CharField(max_length=40)

    def __str__(self):
        return self.type

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type
        }

    class Meta:
        ordering = ['type']


class Role(models.Model):
    function = models.CharField(max_length=50)

    def __str__(self):
        return self.function

    def to_dict(self):
        return {
            'id': self.id,
            'function': self.function
        }

    class Meta:
        ordering = ['function']


class Person(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    title = models.CharField(max_length=35, blank=True, null=True)

    def __str__(self):
        name = ''
        title = ''
        if self.title:
            title = self.title
        first_name = ''
        if self.first_name:
            first_name = self.first_name

        if first_name and not title:
            name = "{last}, {first} {title}".format(
                title=title,
                first=first_name,
                last=self.last_name
            ).strip()
        elif first_name and title:
            name = "{last}, {first}, {title}".format(
                title=title,
                first=first_name,
                last=self.last_name
            ).strip()
        elif title and not first_name:
            name = "{last}, {title}".format(
                last=self.last_name,
                title=title
            )
        else:
            name = self.last_name

        return name

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'title': self.title
        }

    class Meta:
        ordering = ['last_name', 'first_name']


class RolePerson(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    source = models.ForeignKey('Source', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'role': self.role.to_dict(),
            'person': self.person.to_dict(),
        }


class PersonAlias(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    title = models.CharField(max_length=35, null=True)

    def __str__(self):
        title = ''
        if self.title:
            title = self.title
        first_name = ''
        if self.first_name:
            first_name = self.first_name

        return "{title} {first} {last}".format(
            title=title,
            first=first_name,
            last=self.last_name
        ).strip()

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'title': self.title
        }

    class Meta:
        ordering = ['last_name', 'first_name']


# CITIES
class Location(models.Model):
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.country

    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country
        }

    class Meta:
        ordering = ['country']


class LocationAlias(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.country

    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country
        }

    class Meta:
        ordering = ['country']


class Period(models.Model):
    years = models.CharField(max_length=20)
    common_name = models.CharField(max_length=40)

    def __str__(self):
        return "{name} ({years})".format(
            name=self.common_name,
            years=self.years
        )

    def to_dict(self):
        return {
            'id': self.id,
            'years': self.years,
            'common_name': self.common_name
        }

    class Meta:
        ordering = ['common_name']


class Relation(models.Model):
    relationship = models.CharField(max_length=100)

    def __str__(self):
        return self.relationship

    def to_dict(self):
        return {
            'id': self.id,
            'relationship': self.relationship
        }

    class Meta:
       ordering = ['-relationship']


class RelationSource(models.Model):
    relationship = models.ForeignKey(Relation, on_delete=models.CASCADE)
    from_source = models.ForeignKey('Source', related_name='from_source', on_delete=models.CASCADE)
    to_source = models.ForeignKey('Source', related_name='to_source', on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'relationship': self.relationship.to_dict(),
            'to_source': self.to_source.to_dict(),
        }

    class Meta:
        unique_together = ('relationship', 'from_source', 'to_source')


class Source(models.Model):
    title = models.CharField(max_length=400)
    container = models.CharField(max_length=400, blank=True, null=True, verbose_name='Contained in')
    institution = models.CharField(max_length=400, blank=True, null=True, verbose_name='Private Notes')
    series_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Serial Title')
    series_number = models.IntegerField(blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)
    volume_number = models.IntegerField(blank=True, null=True)
    issue = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    pages = models.CharField(max_length=50, blank=True, null=True, verbose_name='Location Details')
    publisher = models.ForeignKey(Publisher, blank=True, null=True, on_delete=models.SET_NULL)
    pub_year = models.CharField(max_length=50, blank=True, null=True, verbose_name='Date')
    doi = models.CharField(max_length=200, blank=True, null=True, verbose_name='Identifying Numbers')
    primary_language = models.ForeignKey(Language, blank=True, null=True, on_delete=models.SET_NULL, related_name="primary_language", verbose_name='Primary Language')
    languages = models.ManyToManyField(Language, blank=True, verbose_name='Languages')
    primary_genre = models.ForeignKey(Field, blank=True, null=True, on_delete=models.SET_NULL, related_name="primary_genre", verbose_name='Primary Genre')
    fields = models.ManyToManyField(Field, blank=True, verbose_name='Genre or Type Descriptor(s)')
    formats = models.ManyToManyField(Format, blank=True)
    roles = models.ManyToManyField(Role, through=RolePerson, blank=True)
    locations = models.ManyToManyField(Location, blank=True, verbose_name='City')
    periods = models.ManyToManyField(Period, blank=True)
    relationships = models.ManyToManyField('self', through=RelationSource, symmetrical=False, blank=True, related_name='related_sources+')
    notes = models.TextField(blank=True, null=True, verbose_name='Descriptive Notes')
    notes2 = models.TextField(blank=True, null=True, verbose_name='Scholarship')
    notes3 = models.TextField(blank=True, null=True, verbose_name='Notes on Prior Documentation')
    notes4 = models.TextField(blank=True, null=True, verbose_name='Authentication')

    def __str__(self):
        first_agent = ""
        try:
            first_agent = ", " + str(self.roleperson_set.all()[0].person)
        except:
            first_agent = ""
        label = "{0}{1} ({2})".format(self.title[:200], first_agent, self.pub_year)
        return label

    def to_dict(self):
        pub_year = ''
        if self.pub_year:
            pub_year = str(self.pub_year.year)

        return {
            'id': self.id,
            'title': self.title,
            'container': self.container,
            'institution': self.institution,
            'series_title': self.series_title,
            'series_number': self.series_number,
            'volume': self.volume,
            'volume_number': self.volume_number,
            'issue': self.issue,
            'edition': self.edition,
            'pages': self.pages,
            'publisher': getattr(self, 'publisher', '').__str__(),
            'pub_year': pub_year,
            'doi': self.doi,
            'language': getattr(self, 'language', '').__str__(),
            'fields': [f.to_dict() for f in self.fields.all()],
            'formats': [f.to_dict() for f in self.formats.all()],
            'roles': [r.to_dict() for r in self.roleperson_set.all()],
            'locations': [l.to_dict() for l in self.locations.all()],
            'periods': [p.to_dict() for p in self.periods.all()]
        }

    class Meta:
        ordering = ['title']


class HTMLBlock(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True, null=True)
    order = models.IntegerField(default=0)
    content = models.TextField(blank=True, null=True, verbose_name='Content')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['order']


def _clear_cache():
    cache.set('sources_datatables', [])

@receiver(post_save, sender=Source)
def source_post_save(sender, instance, **kwargs):
    _clear_cache()

@receiver(post_save, sender=Person)
def person_post_save(sender, instance, **kwargs):
    _clear_cache()