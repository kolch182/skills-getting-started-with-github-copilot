"""
Tests for the Mergington High School Activities API

Uses the Arrange-Act-Assert (AAA) pattern for structured test organization.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that /activities returns all 9 activities with correct structure"""
        # Arrange
        expected_activities_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activities_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities


class TestGetActivitiesDetails:
    """Tests for activity data structure"""
    
    def test_activity_contains_required_fields(self, client):
        """Test that each activity has all required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_details in activities.items():
            assert activity_details.keys() >= required_fields, \
                f"Activity '{activity_name}' missing required fields"
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client):
        """Test successfully signing up a new participant"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert new_email in final_response.json()[activity_name]["participants"]
    
    def test_signup_with_different_activity(self, client):
        """Test signing up for a different activity"""
        # Arrange
        activity_name = "Programming Class"
        email = "testuser@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        verify_response = client.get("/activities")
        assert email in verify_response.json()[activity_name]["participants"]


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client):
        """Test successfully unregistering an existing participant"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert email_to_remove not in final_response.json()[activity_name]["participants"]
    
    def test_unregister_from_different_activity(self, client):
        """Test unregistering from various activities"""
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        verify_response = client.get("/activities")
        assert email not in verify_response.json()[activity_name]["participants"]


class TestRootRedirect:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that / redirects to /static/index.html"""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
