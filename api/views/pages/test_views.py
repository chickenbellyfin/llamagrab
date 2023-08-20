from sanic import Request, Sanic
from sanic_ext import render


def add_views(app: Sanic, **kwargs):
  @app.get('/testpage')
  async def testpage(request: Request):
    return await render(
      "testpage.html",
      context={
        'servers': [
          {'id': 1, 'name': 'NA TDM West', 'status': 'running', 'region_name': 'NA Central', 'owner': 'admin', 'game': 'tribes_ascend_ootb'},
          {'id': 2, 'name': 'NA Mixer', 'status': 'disabled', 'region_name': 'NA Central', 'owner': 'admin', 'game': 'tribes_ascend_ootb'},
          {'id': 2, 'name': '24/7 Stonehenge', 'status': 'disabled', 'region_name': 'NA Central', 'owner': 'admin', 'game': 'tribes_ascend_goty'},
        ],
        'running': [
          {'id': 1, 'name': 'NA TDM West', 'status': 'running', 'region_name': 'NA Central', 'owner': 'admin'},
          {'id': 2, 'name': 'NA Mixer', 'status': 'starting', 'region_name': 'NA Central', 'owner': 'admin'},
          {'id': 3, 'name': '24/7 Stonehenge', 'status': 'restarting', 'region_name': 'NA Central', 'owner': 'admin'},
          {'id': 3, 'name': 'Arena', 'status': 'stopping', 'region_name': 'NA Central', 'owner': 'admin'},
          {'id': 3, 'name': 'Arena', 'status': 'unknown', 'region_name': 'NA Central', 'owner': 'admin'},
        ],
        'users': [
          {'id': 1, 'name': 'chicken', 'tier': 'super', 'limit': '6 / inf'},
          {'id': 2, 'name': 'testadmin', 'tier': 'admin', 'limit': '2 / inf'},
          {'id': 3, 'name': 'testverif', 'tier': 'verified', 'limit': '2 / 5'},
          {'id': 5, 'name': 'testunvrf', 'tier': 'unverified', 'limit': '0 / 1'},
        ]
      }
    )