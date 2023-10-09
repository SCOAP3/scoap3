from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_custom_groups():
    api_user_group, created = Group.objects.get_or_create(name="API_user")
    advanced_user_group, created = Group.objects.get_or_create(name="Advanced_user")
    admin_group, created = Group.objects.get_or_create(name="Admin")

    article_content_type = ContentType.objects.get(
        app_label="articles", model="article"
    )

    add_permission = Permission.objects.get(
        codename="add_article", content_type=article_content_type
    )
    change_permission = Permission.objects.get(
        codename="change_article", content_type=article_content_type
    )
    delete_permission = Permission.objects.get(
        codename="delete_article", content_type=article_content_type
    )

    api_user_group.permissions.add(add_permission)
    advanced_user_group.permissions.add(add_permission, change_permission)
    admin_group.permissions.add(add_permission, change_permission, delete_permission)

    return api_user_group, advanced_user_group, admin_group