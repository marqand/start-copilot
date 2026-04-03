"""
FastAPI Backend Tests for High School Management System

Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities"""
        # Arrange - Test client is set up via fixture

        # Act - Make GET request to activities endpoint
        response = client.get("/activities")

        # Assert - Verify response structure and data
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # All 9 activities should be present

        # Verify structure of first activity (Chess Club)
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        # Note: Don't check exact count as other tests may modify it


class TestRootEndpoint:
    """Test GET / endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        # Arrange - Test client is set up via fixture

        # Act - Make GET request to root endpoint (don't follow redirects)
        response = client.get("/", follow_redirects=False)

        # Assert - Verify redirect response
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange - Prepare test data (use activity with no initial participants)
        activity_name = "Basketball Team"
        email = "test@mergington.edu"

        # Act - Make POST request to signup endpoint
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Verify successful signup
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity_name}" in data["message"]

        # Verify participant was added to activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        # Arrange - Use invalid activity name
        activity_name = "NonExistent Club"
        email = "test@mergington.edu"

        # Act - Attempt to signup for invalid activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Verify 404 error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        """Test duplicate signup returns 400 error"""
        # Arrange - Use activity with initial participants
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act - Attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert - Verify 400 error for duplicate
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is already signed up" in data["detail"]

    def test_signup_empty_activity_name(self, client):
        """Test signup with empty activity name"""
        # Arrange - Empty activity name
        activity_name = ""
        email = "test@mergington.edu"

        # Act - Attempt signup with empty activity name
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Should return 404 for non-existent activity
        assert response.status_code == 404

    def test_signup_empty_email(self, client):
        """Test signup with empty email"""
        # Arrange - Valid activity but empty email
        activity_name = "Drama Club"
        email = ""

        # Act - Attempt signup with empty email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Should succeed (no email validation currently)
        assert response.status_code == 200
        data = response.json()
        assert "" in data["message"]  # Empty email in message


class TestDeleteParticipantEndpoint:
    """Test DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_participant_success(self, client):
        """Test successful removal of a participant"""
        # Arrange - Use activity with initial participants
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Verify participant exists initially
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        initial_count = len(activities[activity_name]["participants"])

        # Act - Delete the participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert - Verify successful deletion
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Removed {email} from {activity_name}" in data["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_delete_participant_nonexistent_activity(self, client):
        """Test deletion from non-existent activity returns 404"""
        # Arrange - Use invalid activity name
        activity_name = "Fake Club"
        email = "test@mergington.edu"

        # Act - Attempt to delete from invalid activity
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert - Verify 404 error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_delete_participant_not_found(self, client):
        """Test deletion of non-existent participant returns 404"""
        # Arrange - Valid activity but non-existent participant
        activity_name = "Debate Club"
        email = "nonexistent@mergington.edu"

        # Act - Attempt to delete non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert - Verify 404 error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_delete_participant_empty_activity(self, client):
        """Test deletion with empty activity name"""
        # Arrange - Empty activity name
        activity_name = ""
        email = "test@mergington.edu"

        # Act - Attempt deletion with empty activity name
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert - Should return 404
        assert response.status_code == 404

    def test_delete_participant_empty_email(self, client):
        """Test deletion with empty email"""
        # Arrange - Valid activity but empty email
        activity_name = "Science Club"
        email = ""

        # Act - Attempt deletion with empty email
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert - Should return 404 (participant not found)
        assert response.status_code == 404


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""

    def test_multiple_signups_and_deletions(self, client):
        """Test multiple signups and deletions work correctly"""
        # Arrange - Test data (use empty activity)
        activity_name = "Soccer Club"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]

        # Act & Assert - Multiple signups
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all participants added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        for email in emails:
            assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3

        # Act & Assert - Remove middle participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{emails[1]}"
        )
        assert response.status_code == 200

        # Verify participant removed but others remain
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert emails[1] not in activities[activity_name]["participants"]
        assert emails[0] in activities[activity_name]["participants"]
        assert emails[2] in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 2

    def test_activity_participant_count_accuracy(self, client):
        """Test that participant counts are accurate after operations"""
        # Arrange - Start with activity that has participants
        activity_name = "Programming Class"

        # Get initial count
        activities_response = client.get("/activities")
        initial_activities = activities_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act - Add a participant
        new_email = "newplayer@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        assert response.status_code == 200

        # Assert - Verify count increased
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert new_email in activities[activity_name]["participants"]

        # Act - Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{new_email}"
        )
        assert response.status_code == 200

        # Assert - Verify count returned to original
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == initial_count
        assert new_email not in activities[activity_name]["participants"]