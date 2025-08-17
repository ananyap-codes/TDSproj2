"""
Basic tests for the Data Analyst Agent API
"""

import pytest
import json
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_capabilities_endpoint(client):
    """Test the capabilities endpoint"""
    response = client.get('/api/capabilities')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'supported_file_types' in data
    assert 'analysis_capabilities' in data

def test_missing_questions_file(client):
    """Test API with missing questions.txt file"""
    response = client.post('/api/', data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Add more tests as needed
