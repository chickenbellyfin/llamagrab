import pytest
from schema.game_server_config import GameServerConfig


def test_all_fields_optional():
  result = GameServerConfig.parse("{}")
  assert result is not None