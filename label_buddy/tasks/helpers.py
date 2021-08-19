from datetime import datetime

from users.models import User
from projects.models import Project
from .models import (
    Annotation,
    Task,
    Status,
    Comment,
    Annotation_status,
)

# get user by username
def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None

# get annotation by task, project and user
def get_annotation(task, project, user):
    try:
        annotation = Annotation.objects.get(task=task, project=project, user=user)
        return annotation
    except Annotation.DoesNotExist:
        return None

def get_review(annotation):
    try:
        review = Comment.objects.get(annotation=annotation)
        return review
    except Comment.DoesNotExist:
        return None

# export data for project
def export_data(project, export_only_approved):
    """
    for all tasks of project which have been annotated.
    Result will be an array of dicts. Each dict will represent a task
    which will contain all annotation completed for this task.
    """
    exported_result = []
    skipped_annotations = 0
    # get all annotated tasks of project
    annotated_tasks = Task.objects.filter(project=project, status=Status.labeled)

    for task in annotated_tasks:
        task_dict = {
            "id": task.id,
            "annotations": [],
            "file_upload": task.original_file_name,
            "data": {
                "audio": task.file.url,
            },
            "project_created_at": project.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "project": project.id,
        }

        task_annotations = Annotation.objects.filter(task=task, project=project)

        # for every annotation, push it
        for annotation in task_annotations:
            if export_only_approved:
                if annotation.review_status == Annotation_status.approved:
                    annotation_user = annotation.user
                    review = get_review(annotation)
                    assert review is not None, "Annotation approved but not reviewed"
                    annotation_dict = {
                        "id": annotation.id,
                        "completed_by": {
                            "id": annotation_user.id,
                            "username": annotation_user.username,
                            "email": annotation_user.email,
                            "name": annotation_user.name,
                        },
                        "reviewed_by": {} if not review else {
                            "id": review.reviewed_by.id,
                            "username": review.reviewed_by.username,
                            "email": review.reviewed_by.email,
                            "name": review.reviewed_by.name,
                            "review_status": annotation.review_status.name,
                            "review_created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "review_updated_at": review.updated_at.strftime("%Y-%m-%d %H:%M:%S") if review.updated_at else "",
                        },
                        "result": annotation.result,
                        "created_at": annotation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": annotation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if annotation.updated_at else "",
                        "task": task.id,
                    }
                    task_dict["annotations"].append(annotation_dict)
                else:
                    skipped_annotations += 1
            else:
                annotation_user = annotation.user
                review = get_review(annotation)
                annotation_dict = {
                    "id": annotation.id,
                    "completed_by":{
                        "id": annotation_user.id,
                        "username": annotation_user.username,
                        "email": annotation_user.email,
                        "name": annotation_user.name,
                    },
                    "reviewed_by": {} if not review else {
                        "id": review.reviewed_by.id,
                        "username": review.reviewed_by.username,
                        "email": review.reviewed_by.email,
                        "name": review.reviewed_by.name,
                        "review_status": annotation.review_status.name,
                        "review_created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "review_updated_at": review.updated_at.strftime("%Y-%m-%d %H:%M:%S") if review.updated_at else "",
                    },
                    "result": annotation.result,
                    "created_at": annotation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": annotation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if annotation.updated_at else "",
                    "task": task.id,
                }
                task_dict["annotations"].append(annotation_dict)

        exported_result.append(task_dict)
    return exported_result, skipped_annotations

