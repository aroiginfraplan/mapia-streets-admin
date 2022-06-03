from django.http import HttpResponseRedirect
from django.shortcuts import render

from mstreets.forms import MultiplePoiForm


def apply_edit(modeladmin, request, queryset, fields):
    per_actualitzar = {}
    for field in fields:
        if request.POST.get(field) != '' and request.POST.get(field):
            per_actualitzar[field] = request.POST.get(field)

    if len(list(per_actualitzar.keys())) > 0:
        queryset.update(**per_actualitzar)
        modeladmin.message_user(request, "S'han actualitzat %s objectes" % queryset.count())


def get_valors_field(queryset, field):
    def get_valors(valors, foreign_key=False):
        n = len(valors)
        initial = None
        if n == 1:
            if foreign_key and hasattr(valors[0], 'campaign'):
                initial = valors[0].campaign
            else:
                initial = valors[0]

        diferents = n > 1
        return initial, diferents

    valors_campaign = list(set([getattr(x, field) if getattr(x, field) else None for x in queryset]))
    return get_valors(valors_campaign, foreign_key=True)


def get_valors(queryset, fields):
    initial = {}
    valors_diferents = {}

    for field in fields:
        initial[field], valors_diferents[field] = get_valors_field(queryset, field)
    return initial, valors_diferents


def edit_multiple(modeladmin, request, queryset, Form, fields, action, title):
    if 'apply' in request.POST:
        apply_edit(modeladmin, request, queryset, fields)
        return HttpResponseRedirect(request.get_full_path())

    initial, valors_diferents = get_valors(queryset, fields)
    form = Form(initial)
    return render(
        request,
        'admin/mstreets/edit_multiples.html',
        context={
            'queryset': queryset, 'form': form, 'valors_diferents': valors_diferents,
            'action': action, 'title': title
        }
    )


def edit_multiple_poi(modeladmin, request, queryset):
    Form = MultiplePoiForm
    fields = ['folder', 'type', ]
    action = 'edit_multiple_poi'
    title = 'Edita múltiples punts d\'interès'
    return edit_multiple(modeladmin, request, queryset, Form, fields, action, title)


edit_multiple_poi.short_description = 'Editar els POI seleccionats'
