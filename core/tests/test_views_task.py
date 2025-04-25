from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import User, Project, Task
from rest_framework_simplejwt.tokens import RefreshToken




def get_jwt_token_for_user(user):
    """Helper function to get JWT token for a user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)




class ProjectTestSetup(APITestCase):
    """Test setup class to create users and project for testing tasks"""
    def setUp(self):
        # Create different types of users
        self.admin = User.objects.create_user(
            email='admin@example.com', password='adminpass', name='Admin', role='ADMIN'
        )
        self.pm = User.objects.create_user(
            email='pm@example.com', password='pmpass', name='Project Manager', role='PROJECT_MANAGER'
        )
        self.dev = User.objects.create_user(
            email='dev@example.com', password='devpass', name='Developer', role='DEVELOPER'
        )


        # Create a project and assign members (PM and DEV)
        self.project = Project.objects.create(name='Demo Project', created_by=self.admin)
        self.project.members.add(self.pm, self.dev)




class TaskListCreateTests(ProjectTestSetup):
    """Test suite for listing and creating tasks"""
    def setUp(self):
        super().setUp()
        self.url = reverse('task-list')  # URL for listing tasks


        # Create a sample task with the created_by field set to the admin user
        self.task = Task.objects.create(
            title="Sample Task",
            project=self.project,
            assigned_to=self.pm,
            created_by=self.admin  # Ensure created_by is set to the admin
        )


    def test_admin_can_list_tasks(self):
        print("\nRunning test_admin_can_list_tasks...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_create_task_as_admin(self):
        print("\nRunning test_create_task_as_admin...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        task_data = {
            "title": "New Task",
            "description": "This is a task description",
            "assigned_to": self.pm.id,
            "project": self.project.id,
            "created_by": self.admin.id  # Ensure created_by is included in the task creation
        }
        res = self.client.post(reverse('task-create'), task_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Expected: 201 Created
        print("✅ Test passed.")


    def test_pm_can_list_tasks(self):
        print("\nRunning test_pm_can_list_tasks...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_dev_can_list_tasks(self):
        print("\nRunning test_dev_can_list_tasks...")
        token = get_jwt_token_for_user(self.dev)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_create_task_without_authentication(self):
        print("\nRunning test_create_task_without_authentication...")
        task_data = {
            "title": "Task without Auth",
            "description": "This task should fail without authentication",
            "assigned_to": self.pm.id,
            "project": self.project.id,
            "created_by": self.admin.id  # Ensure created_by is included in the task creation
        }
        res = self.client.post(reverse('task-create'), task_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Expected: 401 Unauthorized
        print("✅ Test passed.")


    def test_create_task_without_required_fields(self):
        print("\nRunning test_create_task_without_required_fields...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        task_data = {
            "title": "Invalid Task"  # Missing other required fields
        }
        res = self.client.post(reverse('task-create'), task_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Expected: 400 Bad Request
        print("✅ Test passed.")


    def test_create_task_with_invalid_data(self):
        print("\nRunning test_create_task_with_invalid_data...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        task_data = {
            "title": "Invalid Task",
            "description": "This task has invalid data",
            "assigned_to": "invalid_user_id",  # Invalid user ID
            "project": "invalid_project_id",   # Invalid project ID
            "created_by": self.admin.id
        }
        res = self.client.post(reverse('task-create'), task_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Expected: 400 Bad Request
        print("✅ Test passed.")


