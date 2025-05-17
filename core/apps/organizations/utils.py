def get_organization_slug(instance) -> str:
    return f"{instance.name}-{instance.uid}"


def get_organization_media_path_prefix(instance, filename) -> str:
    return f"organizations/{instance.slug}/{filename}"
