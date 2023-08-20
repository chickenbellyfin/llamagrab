from . import audit, iplogs, servers, site, users

def add_views(**kwargs):
    audit.add_views(**kwargs)
    iplogs.add_views(**kwargs)
    servers.add_views(**kwargs)
    site.add_views(**kwargs)
    users.add_views(**kwargs)
    