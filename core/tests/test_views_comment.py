from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import User, Project, Task, Comment
from rest_framework_simplejwt.tokens import RefreshToken




def get_jwt_token_for_user(user):
    """Helper function to get JWT token for a user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)




class CommentTestSetup(APITestCase):
    """Test setup class to create users, projects, tasks, and comments for testing"""
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(email='admin@example.com', password='adminpass', role='ADMIN', name='admin')
        self.pm = User.objects.create_user(email='pm@example.com', password='pmpass', role='PROJECT_MANAGER', name='pm12')
        self.dev = User.objects.create_user(email='dev@example.com', password='devpass', role='DEVELOPER', name='dev')
        self.client_user = User.objects.create_user(email='client@example.com', password='clientpass', role='CLIENT', name='client')


        # Create a project and assign members (PM and DEV)
        self.project = Project.objects.create(name='Demo Project', created_by=self.admin)
        self.project.members.add(self.pm, self.dev)


        # Create a task in the project
        self.task = Task.objects.create(title="Sample Task", project=self.project, assigned_to=self.pm, created_by=self.admin)


        # Create a comment for the task
        self.comment = Comment.objects.create(content="This is a comment", task=self.task, project=self.project, created_by=self.pm)




class CommentCreateTests(CommentTestSetup):
    """Test suite for creating comments"""
    def setUp(self):
        super().setUp()
        self.url = reverse('comment-create')  # URL for creating commeest_pm_can_delete_comment_on_own_projectnts


    def test_create_comment_as_authenticated_user(self):
        print("\nRunning test_create_comment_as_authenticated_user...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        comment_data = {
            "content": "This is a new comment",
            "project": self.project.id,
            "task": self.task.id
        }
        res = self.client.post(self.url, comment_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        print("✅ Test passed.")


    def test_create_comment_without_content(self):
        print("\nRunning test_create_comment_without_content...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        comment_data = {
            "project": self.project.id,
            "task": self.task.id
        }
        res = self.client.post(self.url, comment_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        print("✅ Test passed.")


    def test_create_comment_without_project_or_task(self):
        print("\nRunning test_create_comment_without_project_or_task...")
        token = get_jwt_token_for_user(self.pm)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        comment_data = {
            "content": "This is an invalid comment"
        }
        res = self.client.post(self.url, comment_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        print("✅ Test passed.")


    def test_create_comment_as_user_not_in_project(self):
        print("\nRunning test_create_comment_as_user_not_in_project...")
        token = get_jwt_token_for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        comment_data = {
            "content": "This is a comment",
            "project": self.project.id,
            "task": self.task.id
        }
        res = self.client.post(self.url, comment_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Test passed.")




class CommentListTests(CommentTestSetup):
    """Test suite for listing comments"""
    def setUp(self):
        super().setUp()
        self.url = reverse('comment-list')  # URL for listing comments


    def test_admin_can_list_all_comments(self):
        print("\nRunning test_admin_can_list_all_comments...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print("✅ Test passed.")



class CommentDeleteTests(CommentTestSetup):
    """Test suite for deleting comments"""
    def setUp(self):
        super().setUp()
        self.url = reverse('comment-delete', kwargs={'pk': self.comment.id})  # URL for deleting comments


    def test_admin_can_delete_any_comment(self):
        print("\nRunning test_admin_can_delete_any_comment...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.delete(self.url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        print("✅ Test passed.")



    def test_dev_cannot_delete_comment_on_another_task(self):
        print("\nRunning test_dev_cannot_delete_comment_on_another_task...")
        token = get_jwt_token_for_user(self.dev)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('comment-delete', kwargs={'pk': 99999})  # Invalid comment ID
        res = self.client.delete(url)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        print("✅ Test passed.")




class CommentUpdateTests(CommentTestSetup):
    """Test suite for updating comments"""
    def setUp(self):
        super().setUp()
        self.url = reverse('comment-update', kwargs={'pk': self.comment.id})  # URL for updating comments


    def test_admin_can_update_any_comment(self):
        print("\nRunning test_admin_can_update_any_comment...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        comment_data = {"content": "Updated comment content"}
        res = self.client.put(self.url, comment_data)
        print(f"Response: {res.status_code}, {res.data}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print("✅ Test passed.")