"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Tests for activities endpoints"""

    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_signup_for_activity_success(self):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Signed up" in result["message"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@mergington.edu"
        activity = "Chess Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_success(self):
        """Test successfully unregistering from an activity"""
        email = "unregister_test@mergington.edu"
        activity = "Tennis Club"
        
        # First, sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        result = unregister_response.json()
        assert "Unregistered" in result["message"]
        
        # Verify participant is removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_not_registered(self):
        """Test unregister when not registered"""
        response = client.delete(
            "/activities/Debate Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_root_redirect(self):
        """Test that root path redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
