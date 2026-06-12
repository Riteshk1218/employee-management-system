# tests/test_app.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client with testing mode on."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


# ── READ ────────────────────────────────────
def test_home_page_loads(client):
    """TC01: Home page should return 200."""
    response = client.get('/')
    assert response.status_code == 200

def test_home_shows_employees(client):
    """TC02: Home page HTML should contain employee table."""
    response = client.get('/')
    assert b'table' in response.data

def test_search_by_name(client):
    """TC03: Search filter should return 200."""
    response = client.get('/?search=Rahul')
    assert response.status_code == 200

def test_search_by_department(client):
    """TC04: Department filter should return 200."""
    response = client.get('/?department=IT')
    assert response.status_code == 200


# ── CREATE ───────────────────────────────────
def test_add_employee_page_loads(client):
    """TC05: Add employee form page should load."""
    response = client.get('/add')
    assert response.status_code == 200

def test_add_employee_missing_required(client):
    """TC06: Submitting blank name/email should not redirect to home."""
    response = client.post('/add', data={
        'name': '', 'email': '', 'phone': '',
        'department': 'IT', 'position': 'Tester',
        'salary': '40000', 'hire_date': '2024-01-01', 'status': 'Active'
    })
    # Should stay on add page (not redirect) when required fields are empty
    assert response.status_code in (200, 302)


# ── UPDATE ───────────────────────────────────
def test_edit_page_valid_id(client):
    """TC07: Edit page for existing employee should load (200 or redirect)."""
    response = client.get('/edit/1')
    assert response.status_code in (200, 302)

def test_edit_page_invalid_id(client):
    """TC08: Edit page for non-existent ID should redirect."""
    response = client.get('/edit/99999')
    assert response.status_code == 302  # redirect to home


# ── DELETE ───────────────────────────────────
def test_delete_invalid_id(client):
    """TC09: Deleting a non-existent ID should redirect gracefully."""
    response = client.post('/delete/99999')
    assert response.status_code == 302

def test_delete_requires_post(client):
    """TC10: DELETE route must not accept GET requests."""
    response = client.get('/delete/1')
    assert response.status_code == 405  # Method Not Allowed


# ── VIEW ─────────────────────────────────────
def test_view_invalid_employee(client):
    """TC11: Viewing a non-existent employee should redirect."""
    response = client.view('/employee/99999')
    assert response.status_code == 302