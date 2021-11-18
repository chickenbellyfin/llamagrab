def test_get_regions(test_client, test_regions):
  response = test_client.get('/api/data/regions')
  assert response.json() == test_regions