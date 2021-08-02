from users.models import User
from .models import Annotation

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