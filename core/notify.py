from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

# email notify

def notify_tech_lead_on_task_update(task):
    project = task.project
    subject = f"Attention!!! Task Update {task.title} status changed"
    message = f"""
    Hello Tech Lead,


    A task has been updated in project {project.name}:


    Project: {project.name}
    Task: {task.title}
    New Status: {task.status}
    Updated By: {task.assigned_to.name if task.assigned_to else "Unknown"}


    Please check the update progress.


    Regards,
    {task.assigned_to.name if task.assigned_to else "Senior Dev"}    
    Dev Team,
    {project.name}
    """
   
    html_message = f"""
    <html>
    <body>
        <p>Hello Tech Lead,</p>
        <p>A task has been updated in project <strong>{project.name}</strong>:</p>
        <p><strong>Project:</strong> {project.name}<br>
        <strong>Task:</strong> {task.title}<br>
        <strong>New Status:</strong> <span style="background-color: yellow; padding: 2px 5px; font-weight: bold;">{task.status}</span><br>
        <strong>Updated By:</strong> {task.assigned_to.name if task.assigned_to else "Unknown"}</p>
        <p>Please review the update.</p>
        <p>Regards,<br>Dev Team,<br>{project.name}</p>
    </body>
    </html>
    """


    # Filter only TECH_LEAD users in the project
    tech_leads = project.members.filter(role='TECH_LEAD')
    recipient_list = [user.email for user in tech_leads]

    print(f"Tech leads to notify: {recipient_list}")


    if recipient_list:
        try:
            print("Attempting to send email...")
            email_sent = send_mail(
                subject,
                strip_tags(message), 
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
                html_message=html_message  
            )
           
            # Check if the email was sent successfully
            if email_sent:
                print(f"Email successfully sent to: {', '.join(recipient_list)}")
            else:
                print(f"Email was not sent to any recipients: {', '.join(recipient_list)}")
               
        except Exception as e:
            print(f"Error sending email to tech lead for task '{task.title}' in project '{project.name}': {e}")
    else:
        print("No tech leads found for this project.")




