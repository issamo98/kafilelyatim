from django import template

register = template.Library()

@register.filter
def get_level_name(levels, level_id):
    for level in levels:
        if str(level.id) == str(level_id):
            return level.level
    return ""
