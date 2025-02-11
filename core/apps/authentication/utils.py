def get_user_slug(instance):
    return (
        f"{instance.first_name}-{instance.last_name}-{str(instance.uid).split('-')[0]}"
    )


def get_user_media_path_prefix(instance, filename):
    return f"users/{instance.slug}/{filename}"