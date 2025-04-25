from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken




def get_jwt_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)




class BaseTestSetup(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com', password='adminpass', name='Admin', role='ADMIN'
        )
        self.developer = User.objects.create_user(
            email='dev@example.com', password='devpass', name='Developer', role='DEVELOPER'
        )
        self.client_user = User.objects.create_user(
            email='client@example.com', password='clientpass', name='Client User', role='CLIENT'
        )




class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', password='testpass', name='Test User', role='CLIENT'
        )
        self.url = reverse('token_obtain_pair')


    def test_login_success(self):
        print("\nRunning test_login_success...")
        response = self.client.post(self.url, {'email': 'test@example.com', 'password': 'testpass'})
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        print("✅ Test passed.")


    def test_login_failure(self):
        print("\nRunning test_login_failure...")
        response = self.client.post(self.url, {'email': 'test@example.com', 'password': 'wrongpass'})
        print("Status code:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Test passed.")




class CreateUserTest(BaseTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('create-user')


    def test_admin_can_create_user(self):
        print("\nRunning test_admin_can_create_user...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        payload = {
            "email": "new@example.com",
            "password": "newpass123",
            "name": "New User",
            "role": "CLIENT"
        }
        res = self.client.post(self.url, payload)
        print("Response status:", res.status_code, "| Data:", res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        print("✅ Test passed.")


    def test_creation_missing_fields(self):
        print("\nRunning test_creation_missing_fields...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post(self.url, {"email": "new@example.com"})
        print("Response status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        print("✅ Test passed.")




class ListUsersTest(BaseTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('list-users')


    def test_non_admin_cannot_list_users(self):
        print("\nRunning test_non_admin_cannot_list_users...")
        token = get_jwt_token_for_user(self.developer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Test passed.")




class RetrieveUserTest(BaseTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('get-user', kwargs={'id': self.client_user.id})


    def test_admin_can_retrieve_user(self):
        print("\nRunning test_admin_can_retrieve_user...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print("User email:", res.data["email"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.client_user.email)
        print("✅ Test passed.")


    def test_non_admin_cannot_retrieve_user(self):
        print("\nRunning test_non_admin_cannot_retrieve_user...")
        token = get_jwt_token_for_user(self.developer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(self.url)
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Test passed.")




class AdminUpdateUserTest(BaseTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('admin-update-user', kwargs={'id': self.client_user.id})


    def test_non_admin_cannot_update_other_user(self):
        print("\nRunning test_non_admin_cannot_update_other_user...")
        token = get_jwt_token_for_user(self.developer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.put(self.url, {"name": "Hack"})
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Test passed.")




class UserDeleteTest(BaseTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('delete-user', kwargs={'id': self.client_user.id})


    def test_admin_can_delete_user(self):
        print("\nRunning test_admin_can_delete_user...")
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.delete(self.url)
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print("✅ Test passed.")


    def test_non_admin_cannot_delete_user(self):
        print("\nRunning test_non_admin_cannot_delete_user...")
        token = get_jwt_token_for_user(self.developer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.delete(self.url)
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print("✅ Test passed.")




class UserSelfUpdateTest(BaseTestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('user-self-update')


    def test_unauthenticated_cannot_update_self(self):
        print("\nRunning test_unauthenticated_cannot_update_self...")
        res = self.client.put(self.url, {"name": "Should Fail"})
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Test passed.")




class InvalidUserOperationsTest(BaseTestSetup):
    def test_admin_gets_404_for_invalid_user_id(self):
        print("\nRunning test_admin_gets_404_for_invalid_user_id...")
        url = reverse('get-user', kwargs={'id': 999})
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(url)
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        print("✅ Test passed.")


    def test_delete_invalid_user(self):
        print("\nRunning test_delete_invalid_user...")
        url = reverse('delete-user', kwargs={'id': 999})
        token = get_jwt_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.delete(url)
        print("Status:", res.status_code)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        print("✅ Test passed.")
