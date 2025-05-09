from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        avatar_file = request.FILES['avatar']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Only JPEG, PNG and GIF are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique filename
        ext = os.path.splitext(avatar_file.name)[1]
        filename = f'avatars/{uuid.uuid4()}{ext}'

        # Delete old avatar if exists
        if request.user.avatar:
            try:
                default_storage.delete(request.user.avatar.name)
            except:
                pass

        # Save new avatar
        path = default_storage.save(filename, ContentFile(avatar_file.read()))
        request.user.avatar = path
        request.user.save()

        return Response({
            'avatar': request.user.avatar.url
        }, status=status.HTTP_200_OK) 