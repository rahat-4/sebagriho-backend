from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(required=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "uid",
            "slug",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "date_of_birth",
            "blood_group",
            "is_owner",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                return
        self.fields.pop("is_owner")

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = (
            User.objects.filter(phone=identifier).first()
            or User.objects.filter(email=identifier).first()
        )

        if user is None:
            raise serializers.ValidationError(
                {"identifier": "User with this identifier does not exist."}
            )

        user = authenticate(username=user.phone, password=password)

        if user is None:
            raise serializers.ValidationError({"password": "Password is incorrect."})

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {"user": user, "refresh": refresh, "access_token": access_token}
