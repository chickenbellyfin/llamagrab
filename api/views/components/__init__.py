from . import server_card, region_status

def add_views(**kwargs):
    server_card.add_views(**kwargs)
    region_status.add_views(**kwargs)