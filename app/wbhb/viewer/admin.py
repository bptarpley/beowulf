from django.contrib import admin
from django import forms
from .models import *
from tinymce.widgets import TinyMCE


# HTML Block
@admin.register(HTMLBlock)
class HTMLBlockAdmin(admin.ModelAdmin):
    verbose_name = 'Page'
    verbose_name_plural = 'Pages'
    formfield_overrides = {
        models.TextField: {
            'widget': TinyMCE(attrs={'rows': 40, 'cols': 80})
        }
    }


# PUBLISHER
@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ('press',)


# LANGUAGE
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


# FIELD
@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    verbose_name = 'Genre'
    verbose_name_plural = 'Genres'


#class FieldsInline(admin.TabularInline):
#    model = Source.fields.through
#    extra = 1
#    model._meta.verbose_name_plural = 'Genres'
#    model._meta.verbose_name = 'Genre'


# FORMAT
@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    pass


# ROLE
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


# PERSON
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'title',)


class RolePersonAdmin(admin.TabularInline):
    model = RolePerson
    extra = 1

# RELATIONSHIP
@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    pass

class RelationSourceAdmin(admin.TabularInline):
    model = RelationSource
    extra = 1
    fk_name = 'from_source'
    search_fields = ['relationship', 'to_source']
    autocomplete_fields = ['to_source']


@admin.register(PersonAlias)
class PersonAliasAdmin(admin.ModelAdmin):
    pass


# LOCATION
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(LocationAlias)
class LocationAliasAdmin(admin.ModelAdmin):
    pass


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    inlines = (RolePersonAdmin, RelationSourceAdmin)
    filter_horizontal = ('languages', 'fields')
    search_fields = ('title', 'container', 'institution', 'series_title', 'roleperson__person__last_name', 'roleperson__person__first_name', 'doi')
    exclude = ('periods',)
    formfield_overrides = {
        models.TextField: {
            'widget': TinyMCE(attrs={'rows': 20, 'cols': 80})
        }
    }
