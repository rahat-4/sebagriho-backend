def get_organization_slug(instance)->str:
    return f"{instance.name}-{instance.uid}"