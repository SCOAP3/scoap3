from django.contrib.auth.models import Group, Permission

permissions = [
    ("add_article", "Can add article"),
    ("update_article", "Can update article"),
    ("delete_article", "Can delete article"),
    ("view_article", "Can view article"),
    ]

def assign_permissions():
    admin_group, created = Group.objects.get_or_create(name='Admin')
    curator_group, created = Group.objects.get_or_create(name='Curator')
    user_group, created = Group.objects.get_or_create(name='User')

    permission1 = Permission.objects.get(codename='add_article')
    permission2 = Permission.objects.get(codename='update_article')
    permission3 = Permission.objects.get(codename='delete_article')
    permission4 = Permission.objects.get(codename='view_article')


    admin_group.permissions.add(permission1, permission2, permission3, permission4)
    curator_group.permissions.add(permission1, permission2, permission4)
    user_group.permissions.add(permission4)

    return {"admin_group": admin_group, "curator_group": curator_group, "user_group": user_group}
