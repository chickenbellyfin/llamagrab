from pytest import raises

from api.schema.validations import validate_string


def test_string_allowed():
  assert validate_string('') is not None
  assert validate_string(' ') is not None
  assert validate_string("[CLAN] *MY server's, 0* | status:yes w/o/w") is not None
  assert validate_string('llamagrab.net') is not None
  assert validate_string('A' * 500) is not None


def test_string_not_allowed():
  with raises(ValueError):
    validate_string('not;allowed')

  with raises(ValueError):
    validate_string('not)allowed')

  with raises(ValueError):
    validate_string('not(allo)wed')

  with raises(ValueError):
    validate_string('no"t allowed')

  with raises(ValueError):
    validate_string('A' * 501)