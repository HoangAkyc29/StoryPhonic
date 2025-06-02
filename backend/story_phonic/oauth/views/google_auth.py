from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from oauth.models import User
from oauth.serializers import UserSerializer
from rest_framework.permissions import AllowAny

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = f"{settings.FRONTEND_URL}/auth/google/callback"
    client_class = OAuth2Client

class GoogleCallbackView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            # Get user info from Google
            user_info = request.data.get('user_info')
            if not user_info:
                return Response({'error': 'No user info provided'}, status=status.HTTP_400_BAD_REQUEST)

            email = user_info.get('email')
            if not email:
                return Response({'error': 'No email provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'active': True
                }
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 