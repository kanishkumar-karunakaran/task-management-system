# users/urls.py

from django.urls import path
from .views import (
    CreateUserView, CustomLoginView,
    ListUsersView, RetrieveUserView,
    AdminUpdateUserView, UserSelfUpdateView,
    UserDeleteView, ProjectDetailView, ProjectListCreateView, ProjectDeleteView, ProjectUpdateView, TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    TaskDeleteView, CommentCreateView, CommentDeleteView, CommentListView, DeveloperTaskStatusUpdateView,
    CommentUpdateView )
from core.report import ProjectProgressReportView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'), #POST
    path('users/create/', CreateUserView.as_view(), name='create-user'),  # POST
    path('users/', ListUsersView.as_view(), name='list-users'),    # GET
    path('users/<int:id>/', RetrieveUserView.as_view(), name='get-user'),  # GET
    path('users/<int:id>/update/', AdminUpdateUserView.as_view(), name='admin-update-user'),  # PUT
    path('users/<int:id>/delete/', UserDeleteView.as_view(), name='delete-user'),  # DELETE

    path('users/me/', UserSelfUpdateView.as_view(), name='user-self-update'),  # PUT by user / GET / PATCH

    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<int:id>/update/', ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/progress-report/', ProjectProgressReportView.as_view(), name='project-progress-report'),





    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('tasks/<int:pk>/update-status/', DeveloperTaskStatusUpdateView.as_view(), name='developer-task-status-update'),



    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/create/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),


]




