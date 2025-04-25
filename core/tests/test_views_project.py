from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import User, Project
from rest_framework_simplejwt.tokens import RefreshToken




def get_jwt_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)




class ProjectTestSetup(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com', password='adminpass', name='Admin', role='ADMIN'
        )
        self.pm = User.objects.create_user(
            email='pm@example.com', password='pmpass', name='Project Manager', role='PROJECT_MANAGER'
        )
        self.dev = User.objects.create_user(
            email='dev@example.com', password='devpass', name='Developer', role='DEVELOPER'
        )
        self.project = Project.objects.create(name='Demo Project', created_by=self.admin)
        self.project.members.add(self.pm, self.dev)

class ProjectListCreateTests(ProjectTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-list-create')


    def test_admin_can_list_projects(self):
        print("\nRunning test_admin_can_list_projects...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_pm_can_list_own_projects(self):
        print("\nRunning test_pm_can_list_own_projects...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_filter_projects_by_name(self):
        print("\nRunning test_filter_projects_by_name...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url, {'name': 'Demo'})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_create_project_as_admin(self):
        print("\nRunning test_create_project_as_admin...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post(self.url, {"name": "New Project"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Expected: 201 Created
        print("✅ Test passed.")


    def test_create_project_as_pm(self):
        print("\nRunning test_create_project_as_pm...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post(self.url, {"name": "PM Created Project"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Expected: 201 Created
        print("✅ Test passed.")


    def test_unauthorized_user_cannot_create_project(self):
        print("\nRunning test_unauthorized_user_cannot_create_project...")
        token = get_jwt_token_for_user(self.dev)  # Developer can't create projects
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post(self.url, {"name": "Attempted Project by Developer"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)  # Expected: 403 Forbidden
        print("✅ Test passed.")


    def test_client_cannot_create_project(self):
        print("\nRunning test_client_cannot_create_project...")
        client = User.objects.create_user(
            email='client@example.com', password='clientpass', name='Client', role='CLIENT'
        )
        token = get_jwt_token_for_user(client)  # Client can't create projects
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post(self.url, {"name": "Attempted Project by Client"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)  # Expected: 403 Forbidden
        print("✅ Test passed.")


    def test_unauthenticated_cannot_list_or_create(self):
        print("\nRunning test_unauthenticated_cannot_list_or_create...")
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Expected: 401 Unauthorized
        print("✅ Test passed.")


class ProjectUpdateTests(ProjectTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-update', kwargs={'id': self.project.id})


    def test_admin_can_update_project(self):
        print("\nRunning test_admin_can_update_project...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.put(self.url, {"name": "Updated Project"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_pm_can_update_own_project(self):
        print("\nRunning test_pm_can_update_own_project...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.put(self.url, {"name": "Updated by PM"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_dev_cannot_update_project(self):
        print("\nRunning test_dev_cannot_update_project...")
        token = get_jwt_token_for_user(self.dev)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.put(self.url, {"name": "Hack attempt"})
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)  # Expected: 403 Forbidden
        print("✅ Test passed.")


class ProjectDeleteTests(ProjectTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-delete', kwargs={'pk': self.project.id})


    def test_admin_can_delete_project(self):
        print("\nRunning test_admin_can_delete_project...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.delete(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Expected: 200 OK
        print("✅ Test passed.")


    def test_pm_cannot_delete_project(self):
        print("\nRunning test_pm_cannot_delete_project...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.delete(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)  # Expected: 403 Forbidden
        print("✅ Test passed.")


class ProjectEdgeCases(ProjectTestSetup):
    def test_404_on_nonexistent_project_delete(self):
        print("\nRunning test_404_on_nonexistent_project_delete...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('project-delete', kwargs={'pk': 999})
        res = self.client.delete(url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)  # Expected: 404 Not Found
        print("✅ Test passed.")


