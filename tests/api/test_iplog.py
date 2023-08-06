from unittest.mock import MagicMock
import pytest
from api.audit import AuditLog
from api.database.models import User
from api.host_manager import HostManager
from api.iplog import IPLogDatabase

@pytest.fixture
def host_manager() -> HostManager:
  return MagicMock()

@pytest.fixture
def audit() -> AuditLog:
  return MagicMock()

@pytest.fixture
def admin_user() -> User:
  return User(
    id=1,
    username='test_user_admin',
    password='test_password',
    tier = 'admin'
  )

@pytest.fixture
def non_admin_user() -> User:
  return User(
    id=2,
    username='test_user',
    password='test_password2',
    tier = 'verified'
  )

def test_create_ban(host_manager, audit, admin_user):
  iplog = IPLogDatabase('',  host_manager, audit, db_file_name='') # in memory
  iplog.create_ban('1.2.3.4', 'test_reason', admin_user)
  bans = iplog.get_bans(admin_user)
  assert len(iplog.get_bans(admin_user)) == 1

  iplog.remove_ban(bans[0].id, admin_user)
  assert len(iplog.get_bans(admin_user)) == 0




def test_create_ban_nonadmin(host_manager, audit, admin_user, non_admin_user):
    iplog = IPLogDatabase('',  host_manager, audit, db_file_name='') # in memory 

    try:
      iplog.create_ban('1.2.3.4', 'test_reason', non_admin_user)
      assert False
    except:
      pass

    assert len(iplog.get_bans(admin_user)) == 0
    iplog.create_ban('1.2.3.4', 'test_reason', admin_user)
    ban_id = iplog.get_bans(admin_user)[0].id

    try:
      iplog.remove_ban(ban_id, non_admin_user)
      assert False
    except:
      pass
    
    assert len(iplog.get_bans(admin_user)) == 1 # confirm not deleted