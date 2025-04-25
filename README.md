# Task Management System Documentation

## Authentication

- Uses custom `User` model with JWT-based authentication.
- Roles supported: `ADMIN`, `PROJECT_MANAGER`, `TECH_LEAD`, `DEVELOPER`, `CLIENT`.
- All endpoints are protected; role-based; users must be authenticated.



## Models & Relationships


### User
- `name`: Full name of the user.
- `email`: Unique login credential.
- `role`: Assigned role.
- Related Fields:
  - Can create multiple `Projects` (`created_projects`)
  - Can be member of multiple `Projects` (`projects`)
  - Can create multiple `Tasks` (`created_tasks`)
  - Can be assigned to `Tasks`
  - Can write `Comments`


---


### Project
- `name`: Unique project title.
- `description`: Text description.
- `created_by`: ForeignKey → `User` (creator).
- `members`: ManyToMany → `User` (team members).
- `created_at`: Auto timestamp.
- Related Fields:
  - Has many `Tasks`
  - Has many `Comments` (project-wide)


---


### Task
- `title`: Name of the task.
- `description`: Task content.
- `status`: Status (TODO, IN_PROGRESS, DONE).
- `project`: ForeignKey → `Project`.
- `assigned_to`: ForeignKey → `User` (optional).
- `created_by`: ForeignKey → `User`.
- `created_at`: Auto timestamp.
- Related Fields:
  - Has many `Comments`


---


### Comment
- `content`: Body of the comment.
- `project`: ForeignKey → `Project` (optional).
- `task`: ForeignKey → `Task` (optional).
- `created_by`: ForeignKey → `User`.
- `created_at`, `updated_at`: Auto timestamps.


**Note**: A comment can be attached to any tasks of a project.


---


## Key Relationships Overview

- A **Task** belongs to a **Project**, is created by a **User**, and may be assigned to another **User** (depends on role).

---

## API Overview


All endpoints are protected using JWT authentication and RBAC authorization.  
Use `/login/` to obtain your access and refresh tokens.


---


## Authentication & User Management


- `POST /login/`  
  Authenticate and retrieve JWT tokens (access & refresh)
        
  ```
  METHOD: POST
    {
            "email":"admin@gmail.com",
            "password":"****"
    }
  ```


- `POST /users/create/`  
  Create a new user account (only admin)

```
  METHOD: POST

    {
      "Authorization": "Bearer your_access_token"  // ADMIN
    }

    {
      "email": "user@example.com",
      "name": "John Doe",
      "password": "password123",
      "role": "developer"
    }
```

- `GET /users/`  
  List all users (admin-only)
  {
    "Authorization": "Bearer your_access_token"
  }


- `GET /users/<id>/`  
  Retrieve a specific user's details

      ```
        Method: GET
        Admin updates a specific user
      ```


- `DELETE /users/<id>/delete/`  
  Admin deletes a user


- `GET /users/me/`  
  Get the current authenticated user's profile


- `PUT /users/me/`  
  Update the current user's own profile

      {
      "email": "user@example.com",
      "name": "John Doe Updated",
      "role": "developer"
    }



---


## Project Management


- `GET /projects/`  
  List all projects


- `POST /projects/`  
  Create a new project

      {
      "name": "New Project",
      "description": "This is a description of the new project.",
      "members": [1, 2]  // List of user IDs to associate as members
    }



- `GET /projects/<pk>/`  
  Get details of a specific project


- `PUT /projects/<id>/update/`  
  Update a project's details

      {
        "name": "Updated Project Name",
        "description": "Updated project description.",
        "members": [1, 3]  // Updated list of user IDs as members
      }


- `DELETE /projects/<pk>/delete/`  
  Delete a project


- `GET /projects/<pk>/progress-report/`  
  Download project progress report (PDF or TXT)


---


## Task Management


- `GET /tasks/`  
  List all tasks


- `POST /tasks/create/`  
  Create a new task
      {
        "title": "New Task",
        "description": "This task needs to be completed by the developer.",
        "project": 1,  // ID of the project this task belongs to
        "assigned_to": 2  // ID of the user assigned to this task
      }


- `GET /tasks/<pk>/`  
  View a specific task


- `PUT /tasks/<pk>/update/`  
  Update a task
      
      {
        "title": "Updated Task Title",
        "description": "Updated description for the task.",
        "status": "IN_PROGRESS",
        "assigned_to": 3  // ID of the user assigned to the task
      }

- `DELETE /tasks/<pk>/delete/`  
  Delete a task


- `PATCH /tasks/<pk>/update-status/`  
  Developer updates their assigned task's status
  Email notification sent to Team Lead

      {
      "status": "IN_PROGRESS"
    }



---


## Comment Management


- `GET /comments/`  
  List all comments


- `POST /comments/create/`  
  Create a comment on a task or project

  
        {
          "content": "This is a comment on the task.",
          "project": 1,  // ID of the project the comment belongs to
          "task": 2  // ID of the task the comment belongs to
        }


- `PUT /comments/<pk>/update/`  
  Update an existing comment (by comment id)
    
        {
          "content": "Updated comment content"
        }

- `DELETE /comments/<pk>/delete/`  
  Delete a comment

---


## Project Reports

- Include task status, progress %, and team members.


## Note
- Unit tests are written for all functions
      ```
            Tests Run Command: (model wise)

                python manage.py test core.tests.test_views_user  
                python manage.py test core.tests.test_views_project 
                python manage.py test core.tests.test_views_task  
                python manage.py test core.tests.test_views_command


- Custom error handlled for user email, password fields

    ![image](https://github.com/user-attachments/assets/0527ad87-698a-4d5e-ac82-2187b5be2dca)

  
- Used django pagination (limit and offset as query param)

   ![image](https://github.com/user-attachments/assets/0dcc8876-f986-47a7-8102-637fd1ec96f5)

- Can filter tasks by status
 
     ![image](https://github.com/user-attachments/assets/93d9867c-2e14-459a-a1bd-9f1957440594)

- Search by project name, task title
 
     ![image](https://github.com/user-attachments/assets/67a85d4f-aadb-4532-abe1-76ade6be28c5)


- Integrated mail trap email for notify tech leads about task status
  
    ![image](https://github.com/user-attachments/assets/17c87e25-03b5-4c89-8b35-3f5ebd0a735d)

- Can generate report and view (based on permissions)

       /api/projects/<INT:PK>/progress-report/
  
- Used caching to reduce querying repeated data

    ```
    
       -@method_decorator(cache_page(60 * 2) )


---

## Permissions

![image](https://github.com/user-attachments/assets/f6422343-ee12-4fec-9389-9cccb572582a)





