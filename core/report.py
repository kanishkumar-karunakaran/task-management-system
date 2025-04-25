from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import F
import os
from .models import Project, Task
from .serializers import ProjectSerializer
from datetime import datetime


# Task points based on status
TASK_POINTS = {
    'TODO': 0,
    'IN_PROGRESS': 5,
    'DONE': 10,
}


# Reporting view to generate the project progress report
class ProjectProgressReportView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated] # authentication


    def get_queryset(self):
        return Project.objects.all()


    def get(self, request, *args, **kwargs):
        # Get the project
        project = self.get_object()
        user = request.user


        # Admin can see all projects, otherwise check if the user is part of the project
        if user.role != 'ADMIN' and project not in user.projects.all():
            return Response({"detail": "You do not have permission to view this report."}, status=status.HTTP_403_FORBIDDEN)

        tasks = Task.objects.filter(project=project)


        # Calculate task points and status
        task_details = []
        total_points = 0
        total_tasks = tasks.count()


        for task in tasks:
            points = TASK_POINTS.get(task.status, 0)
            task_details.append({
                'task_title': task.title,
                'status': task.status,
                'points': points
            })
            total_points += points


        # Calculate project progress on a scale of 0 to 100
        if total_tasks > 0:
            project_progress = (total_points / (total_tasks * 10)) * 100  
        else:
            project_progress = 0


        # List of project members
        project_members = project.members.all()
        member_names = [member.name for member in project_members]


        # Prepare the report content as a more detailed text file
        report_content = f"Project Progress Report: {project.name}\n"
        report_content += f"Project Manager: {project.created_by.name}\n"
        report_content += f"Team Members: {', '.join(member_names)}\n\n"
        report_content += "Task Details:\n"


        for task in task_details:
            report_content += f"- Task: {task['task_title']}\n"
            report_content += f"  Status: {task['status']}\n"
            report_content += f"  Points: {task['points']}\n\n"


        report_content += f"Total Tasks: {total_tasks}\n"
        report_content += f"Completed Tasks: {Task.objects.filter(project=project, status='DONE').count()}\n"
        report_content += f"In Progress Tasks: {Task.objects.filter(project=project, status='IN_PROGRESS').count()}\n"
        report_content += f"To Do Tasks: {Task.objects.filter(project=project, status='TODO').count()}\n\n"
        report_content += f"Overall Project Progress: {round(project_progress, 2)}%\n\n"
        
        report_content += f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += "Project Progress depends on task completion. The higher the number of tasks completed, the more progress the project has made.\n"
        report_content += "A task is considered completed when it has the status 'DONE'. Tasks in 'IN_PROGRESS' or 'TODO' represent incomplete work.\n"


        project_folder = os.path.join(settings.MEDIA_ROOT, 'projects', str(project.id))
        os.makedirs(project_folder, exist_ok=True)


        filename = f"project_{project.id}_progress_report.txt"
        file_path = os.path.join(project_folder, filename)


        with open(file_path, 'w') as report_file:
            report_file.write(report_content)


        response = HttpResponse(report_content, content_type="text/plain")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'


        return response




