from django import template

register = template.Library()


@register.filter
def replace_go(string):
    return string.replace(':', '_')

@register.filter
def fix_residue(value):
    return value.replace("_","")

@register.filter
def removeBrackets(value):
    return value.split('{')[0]

@register.filter
def removeOffset(value):
    return value.split('/')[0]

@register.filter
def get0(value):
    return value[0]

@register.filter
def get1(value):
    return value[1]

@register.filter
def keyvalue(dict, key):
    return dict[key]

@register.filter
def hyptest(stringvalue):
    return float(stringvalue) < 1e-05
