from . import pages, components


def add_views(**kwargs):
    pages.add_views(**kwargs)
    components.add_views(**kwargs)