from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Project, Task, Comment
from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
    ProjectSerializer, TaskSerializer, CommentSerializer
)
from .permissions import IsAdminUserJWT, IsAdminOrProjectAccess, IsProjectManagerOrAdmin, IsAdminOrPMOrTL, IsDeveloperUpdatingOwnStatus
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .exceptions import InvalidUserDataException
from .notify import notify_tech_lead_on_task_update
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError, PermissionDenied



class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()


            return Response({
                "message": "User created successfully",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)


        except InvalidUserDataException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        except ValidationError as e:
            missing_fields = [field for field, errors in e.detail.items() if 'This field is required.' in errors]
            if missing_fields:
                return Response({
                    "error": "Missing required fields.",
                    "detail": f"Please provide: {', '.join(missing_fields)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({
                "error": "Something went wrong while creating the user.",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch') 
class ListUsersView(generics.ListAPIView):
    queryset = User.objects.only('id', 'email', 'name', 'role').select_related('profile')  
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserJWT]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)


@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch')
class RetrieveUserView(generics.RetrieveAPIView):
    queryset = User.objects.only('id', 'email', 'name', 'role')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserJWT]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)


class AdminUpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserJWT]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data['message'] = 'User updated successfully'
        return Response(response.data, status=status.HTTP_200_OK)



class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUserJWT]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        self.perform_destroy(user)
        
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)



class UserSelfUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data['message'] = 'Profile updated successfully'
        return Response(response.data, status=status.HTTP_200_OK)



@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch')  # Cache for 2 minutes
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrAdmin]


    def get_queryset(self):
        user = self.request.user
        project_name_filter = self.request.query_params.get('name', None)  # Project name filter
        
        # Start with the base queryset, filtering by project membership
        if user.role == 'ADMIN':
            queryset = Project.objects.all()  # Admin can see all projects
        else:
            queryset = Project.objects.filter(members=user)  # Non-admin users can see projects they are a part of


        # Apply project name filter if provided
        if project_name_filter:
            queryset = queryset.filter(name__icontains=project_name_filter)  # Filter by project name


        return queryset


    def perform_create(self, serializer):
        # When a new project is created, associate it with the current user
        serializer.save(created_by=self.request.user)
        # Custom success message for project creation
        return Response({"message": "Project created successfully"}, status=status.HTTP_201_CREATED)


    def get(self, request, *args, **kwargs):
        # Get filtered projects
        projects = self.get_queryset()
        if projects.exists():
            return Response(self.get_serializer(projects, many=True).data, status=status.HTTP_200_OK)
        return Response({"detail": "No projects found."}, status=status.HTTP_404_NOT_FOUND)



@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch')  # Cache for 2 minutes
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrProjectAccess]
    lookup_field = 'id'


    def get(self, request, *args, **kwargs):
        project = self.get_object()
        return Response(self.get_serializer(project).data, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        project = self.get_object()
        user = request.user


        if user.role == 'ADMIN' or (user.role == 'PROJECT_MANAGER' and user in project.members.all()):
            return super().update(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)


    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        self.perform_destroy(project)
        return Response({"message": "Project deleted successfully"}, status=status.HTTP_200_OK)




class ProjectDeleteView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUserJWT]

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        self.perform_destroy(project)
        return Response({"message": "Project deleted successfully"}, status=status.HTTP_200_OK)



class ProjectUpdateView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


    def update(self, request, *args, **kwargs):
        project = self.get_object()
        user = request.user


        if user.role == 'ADMIN' or (user.role == 'PROJECT_MANAGER' and user in project.members.all()):
            return super().update(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)


# Task List view with caching, project membership, status filtering, and additional search filters
@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch')  # Cache for 2 minutes
class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (SearchFilter,)
    search_fields = ['title', 'project__name']  # Allow searching by task title and project name


    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        task_name_filter = self.request.query_params.get('title', None)  # Correct query parameter for task title
        project_name_filter = self.request.query_params.get('project_name', None)  # Correct query parameter for project name


        # Start with the base queryset, filtering by project membership
        if user.role == 'ADMIN':
            queryset = Task.objects.all()  # Admin can see all tasks
        else:
            queryset = Task.objects.filter(project__members=user) 


        # Apply the status filter if provided
        if status_filter:
            queryset = queryset.filter(status=status_filter)


        # Apply task name filter if provided
        if task_name_filter:
            queryset = queryset.filter(title__icontains=task_name_filter)  # Filter by task title


        # Apply project name filter if provided
        if project_name_filter:
            queryset = queryset.filter(project__name__icontains=project_name_filter)  # Filter by project name


        return queryset


    def get(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        if tasks.exists():
            return Response(self.get_serializer(tasks, many=True).data, status=status.HTTP_200_OK)
        return Response({"detail": "No tasks found."}, status=status.HTTP_404_NOT_FOUND)


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPMOrTL]


    def perform_create(self, serializer):
        title = serializer.validated_data.get('title')
        project = serializer.validated_data.get('project')


        # Check for existing task with the same title under the same project
        if Task.objects.filter(title=title, project=project).exists():
            raise ValidationError("A task with this title already exists in the project.")


        serializer.save(created_by=self.request.user)
        return Response({"message": "Task created successfully"}, status=status.HTTP_201_CREATED)



@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch')  # Cache for 2 minutes
class TaskDetailView(generics.RetrieveAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Task.objects.all()
        return Task.objects.filter(project__members=user)


    def get(self, request, *args, **kwargs):
        task = self.get_object()
        if task:
            return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_permissions(self):
        user = self.request.user
        if user.role in ['ADMIN', 'PROJECT_MANAGER', 'TECH_LEAD']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDeveloperUpdatingOwnStatus()]


    def update(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        if user.role in ['ADMIN', 'PROJECT_MANAGER', 'TECH_LEAD'] or task.assigned_to == user:
            return super().update(request, *args, **kwargs)
        return Response({"detail": "You do not have permission to update this task."},
                        status=status.HTTP_403_FORBIDDEN)


class DeveloperTaskStatusUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']  # Only allow PATCH


    def get_object(self):
        task = super().get_object()
        user = self.request.user
        if user.role != 'DEVELOPER' or task.assigned_to != user:
            raise PermissionDenied("You can only update the status of tasks assigned to you.")
        return task


    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        status_value = request.data.get('status')


        if not status_value:
            return Response({"detail": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)


        valid_statuses = ['TODO', 'IN_PROGRESS', 'DONE']
        if status_value not in valid_statuses:
            return Response({"detail": f"Status must be one of: {', '.join(valid_statuses)}"}, status=status.HTTP_400_BAD_REQUEST)


        task.status = status_value
        task.save()
        notify_tech_lead_on_task_update(task)
        return Response({"detail": "Task status updated successfully."})


from rest_framework.response import Response
from rest_framework import status


class TaskDeleteView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPMOrTL]


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Task deleted successfully."}, status=status.HTTP_200_OK)



class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data


        content = data.get('content')
        project_id = data.get('project')
        task_id = data.get('task')

        if not content:
            return Response({"detail": "The 'content' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not project_id:
            return Response({"detail": "The 'project' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not task_id:
            return Response({"detail": "The 'task' field is required."}, status=status.HTTP_400_BAD_REQUEST)


        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Invalid project ID."}, status=status.HTTP_404_NOT_FOUND)


        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Invalid task ID."}, status=status.HTTP_404_NOT_FOUND)

        if user.role in ['PROJECT_MANAGER', 'TECH_LEAD', 'DEVELOPER', 'CLIENT']:
            if user not in project.members.all():
                return Response({"detail": "You can only comment on projects that you are assigned to."}, 
                                status=status.HTTP_403_FORBIDDEN)

        if Comment.objects.filter(content=content.strip(), created_by=user, project=project, task=task).exists():
            return Response(
                {"detail": "Duplicate comment: You already posted this content for the same task/project."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data={
            "content": content,
            "project": project_id,
            "task": task_id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user)


        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(vary_on_headers("Authorization"), name='dispatch')
@method_decorator(cache_page(60 * 2), name='dispatch') 
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Comment.objects.all()  # Admin can see all comments
        elif user.role == 'PROJECT_MANAGER':
            return Comment.objects.filter(project__created_by=user)  # PM can see comments for their projects
        elif user.role == 'TECH_LEAD':
            return Comment.objects.filter(project__members=user)  # Tech Lead can see comments for assigned projects
        elif user.role == 'DEVELOPER':
            return Comment.objects.filter(task__assigned_to=user)  # Developer can see comments on tasks assigned to them
        elif user.role == 'CLIENT':
            return Comment.objects.filter(project__members=user)  # Clients can see comments for their projects
        return Comment.objects.none()  # Return no comments if role is not recognized


    def get(self, request, *args, **kwargs):
        comments = self.get_queryset()
        if comments.exists():
            return Response(self.get_serializer(comments, many=True).data, status=status.HTTP_200_OK)
        return Response({"detail": "No comments found."}, status=status.HTTP_404_NOT_FOUND)


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


    def perform_destroy(self, instance):
        user = self.request.user
        comment = instance

        # Role-specific delete permissions
        if user.role == 'ADMIN':
            pass  # Admin can delete any comment
        elif user.role == 'PROJECT_MANAGER':
            if comment.project.created_by != user:
                raise PermissionDenied("Project Managers can only delete comments on their own projects.")
        elif user.role == 'TECH_LEAD':
            if user not in comment.project.members.all():
                raise PermissionDenied("Tech Leads can only delete comments from their assigned projects.")
        elif user.role == 'DEVELOPER':
            if comment.created_by != user:
                raise PermissionDenied("Developers can only delete their own comments.")
            if user not in comment.project.members.all():
                raise PermissionDenied("Developers must be assigned to the project to delete a comment.")
        elif user.role == 'CLIENT':
            if user not in comment.project.members.all():
                raise PermissionDenied("Clients can only delete comments from their assigned projects.")
        else:
            raise PermissionDenied("Your role is not allowed to delete comments.")

        comment.delete()
        return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


    def perform_update(self, serializer):
        user = self.request.user
        comment = self.get_object()

        if user.role == 'ADMIN':
            pass  # Admin can update any comment
        elif user.role == 'PROJECT_MANAGER':
            if comment.project.created_by != user:
                raise PermissionDenied("Project Managers can only update comments on their own projects.")
        elif user.role == 'TECH_LEAD':
            if user not in comment.project.members.all():
                raise PermissionDenied("Tech Leads can only update comments from their assigned projects.")
        elif user.role == 'DEVELOPER':
            if comment.created_by != user:
                raise PermissionDenied("Developers can only update their own comments.")
            if user not in comment.project.members.all():
                raise PermissionDenied("Developers must be assigned to the project to update a comment.")
        elif user.role == 'CLIENT':
            if user not in comment.project.members.all():
                raise PermissionDenied("Clients can only update comments from their assigned projects.")
        else:
            raise PermissionDenied("Your role is not allowed to update comments.")
        serializer.save()
        return Response({"detail": "Comment updated successfully."}, status=status.HTTP_200_OK)