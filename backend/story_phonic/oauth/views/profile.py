from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from oauth.serializers.profile import ProfileSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile = request.user.profile
        return Response(ProfileSerializer(profile).data)
    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data) 