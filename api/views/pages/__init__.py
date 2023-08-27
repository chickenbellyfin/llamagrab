from . import admin, index, login, regions, settings, test_views, create_server


def add_views(**kwargs):
    index.add_views(**kwargs)
    login.add_views(**kwargs)
    regions.add_views(**kwargs)
    settings.add_views(**kwargs)
    test_views.add_views(**kwargs)
    create_server.add_views(**kwargs)

    admin.add_views(**kwargs)