from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from scoap3.articles.models import Article


def assign_permissions():
    content_type = ContentType.objects.get_for_model(Article)

    admin_group, created = Group.objects.get_or_create(name="Admin")
    curator_group, created = Group.objects.get_or_create(name="Curator")
    user_group, created = Group.objects.get_or_create(name="User")

    add_permission = Permission.objects.create(
        codename="add_article",
        name="Can add article",
        content_type=content_type,
    )

    change_permission = Permission.objects.create(
        codename="change_article",
        name="Can update article",
        content_type=content_type,
    )

    delete_permission = Permission.objects.create(
        codename="delete_article",
        name="Can delete article",
        content_type=content_type,
    )
    view_permission = Permission.objects.create(
        codename="view_article",
        name="Can view article",
        content_type=content_type,
    )
    add_permission = Permission.objects.get(codename="add_article")
    change_permission = Permission.objects.get(codename="change_article")
    delete_permission = Permission.objects.get(codename="delete_article")
    view_permission = Permission.objects.get(codename="view_permission")

    admin_group.permissions.add(
        add_permission, change_permission, delete_permission, view_permission
    )
    curator_group.permissions.add(add_permission, change_permission, view_permission)
    user_group.permissions.add(view_permission)

    admin_group.save()
    curator_group.save()
    user_group.save()

    return {
        "admin_group": admin_group,
        "curator_group": curator_group,
        "user_group": user_group,
    }
