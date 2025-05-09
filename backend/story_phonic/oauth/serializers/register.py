from rest_framework import serializers
from oauth.models.user import User
from django.contrib.auth.password_validation import validate_password
from oauth.models.role import Role

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'roles')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        roles = validated_data.pop('roles', [])
        user = User.objects.create_user(**validated_data)
        if roles:
            user.roles.set(roles)
        else:
            # Gán role mặc định là 'user'
            user.roles.set([Role.objects.get_or_create(name='user')[0]])
        user.save()
        return user 