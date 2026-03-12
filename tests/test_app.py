import pytest
from fastapi.testclient import TestClient
from app import app, activities

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before each test"""
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and practice sessions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and tournament participation",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucy@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["benjamin@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through experiments and projects",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["charlotte@mergington.edu", "william@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(initial_state)
    yield
    activities.clear()
    activities.update(initial_state)


def test_get_activities(client):
    """Test that GET /activities returns JSON with expected keys"""
    # Arrange: No special setup needed beyond fixture
    
    # Act: Make the GET request
    response = client.get("/activities")
    
    # Assert: Check status and structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    for activity_name, activity_info in data.items():
        assert "description" in activity_info
        assert "schedule" in activity_info
        assert "max_participants" in activity_info
        assert "participants" in activity_info


def test_signup_success(client):
    """Test that POST /activities/{activity_name}/signup successfully adds a participant"""
    # Arrange: Set up test data
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act: Perform the signup
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Check response and state change
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client):
    """Test that POST /activities/{activity_name}/signup returns 400 for duplicate signup"""
    # Arrange: Use an email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act: Attempt duplicate signup
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Check for error response
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_success(client):
    """Test that DELETE /activities/{activity_name}/signup removes a participant"""
    # Arrange: Use an email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act: Perform the unregister
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Check response and state change
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up(client):
    """Test that DELETE /activities/{activity_name}/signup returns 400 for non-signed-up student"""
    # Arrange: Use an email not signed up
    activity_name = "Chess Club"
    email = "notstudent@mergington.edu"
    
    # Act: Attempt to unregister non-participant
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Check for error response
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test that signing up for non-existent activity returns 404"""
    # Arrange: Use a non-existent activity name
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act: Attempt signup for invalid activity
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Check for not found response
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_nonexistent_activity(client):
    """Test that unregistering from non-existent activity returns 404"""
    # Arrange: Use a non-existent activity name
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act: Attempt unregister for invalid activity
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Check for not found response
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]