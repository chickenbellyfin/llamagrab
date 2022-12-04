from fastapi import status
from fastapi.testclient import TestClient


def test_get_regions(test_client: TestClient, test_regions):
  response = test_client.get('/api/data/regions')
  assert response.json() == {
    'region1': 'TestRegion1',
    'region2': 'TestRegion2'
  }

def test_get_status(test_client: TestClient):
  response = test_client.get('/api/status')
  assert response.status_code == status.HTTP_200_OK
