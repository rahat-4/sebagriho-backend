from django.db import models

from common.models import BaseModelWithUid

from .choices import MethodType


class Role(BaseModelWithUid):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        "organizations.organization", on_delete=models.CASCADE, related_name="roles"
    )

    class Meta:
        unique_together = ["name", "organization"]

    def __str__(self):
        return f"{self.organization.name} = {self.name}"


class Permission(BaseModelWithUid):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    methods = models.JSONField(default=list)  # Store multiple methods as a list

    class Meta:
        unique_together = ["role", "methods"]

    def clean(self):
        # Validate that all methods are valid choices
        for method in self.methods:
            if method not in MethodType.values:
                raise ValueError(f"Invalid method: {method}")

    def __str__(self):
        return f"{self.role.name} = {self.methods}"
