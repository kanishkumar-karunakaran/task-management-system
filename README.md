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


- `POST /users/create/`  
  Create a new user account


- `GET /users/`  
  List all users (admin-only)


- `GET /users/<id>/`  
  Retrieve a specific user's details


- `PUT /users/<id>/update/`  
  Admin updates a specific user


- `DELETE /users/<id>/delete/`  
  Admin deletes a user


- `GET /users/me/`  
  Get the current authenticated user's profile


- `PUT /users/me/`  
  Update the current user's own profile


---


## Project Management


- `GET /projects/`  
  List all projects


- `POST /projects/`  
  Create a new project


- `GET /projects/<pk>/`  
  Get details of a specific project


- `PUT /projects/<id>/update/`  
  Update a project's details


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


- `GET /tasks/<pk>/`  
  View a specific task


- `PUT /tasks/<pk>/update/`  
  Update a task


- `DELETE /tasks/<pk>/delete/`  
  Delete a task


- `PATCH /tasks/<pk>/update-status/`  
  Developer updates their assigned task's status

  Email notification sent to Team Lead


---


## Comment Management


- `GET /comments/`  
  List all comments


- `POST /comments/create/`  
  Create a comment on a task or project


- `PUT /comments/<pk>/update/`  
  Update an existing comment


- `DELETE /comments/<pk>/delete/`  
  Delete a comment


## Permissions

![image](https://github.com/user-attachments/assets/4261b977-7d2f-4dc3-8f42-2316d40b1017)


---


## Project Reports

- Include task status, progress %, and team members.


## Note
- Unit tests are written for all functions
- Custom error handlled for user email, password fields
- Used django pagination (limit and offset as query param)
- Can filter tasks by status
- Search by project name, task title
- Integrated mail trap email for notify tech leads about task status
- Can generate report and view (based on permissions)
- Used caching to reduce querying repeated data 


