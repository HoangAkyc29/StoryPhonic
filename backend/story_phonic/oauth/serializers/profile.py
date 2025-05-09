from oauth.models.profile import Profile
from rest_framework import serializers
 
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('full_name', 'avatar', 'bio') 