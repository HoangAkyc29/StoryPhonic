from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.audio_service import upload_audio_to_s3

@api_view(['POST'])
def upload_audio_to_s3_view(request):
    """
    API endpoint to upload audio files to S3
    Expected payload:
    {
        "novel_id": "string",
        "audio_dir": "string"  # Optional, will use default path if not provided
    }
    """
    try:
        novel_id = request.data.get('novel_id')
        if not novel_id:
            return Response(
                {"error": "novel_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_dir = request.data.get('audio_dir')
        
        # Upload files to S3
        uploaded_files = upload_audio_to_s3(novel_id, audio_dir)
        
        return Response({
            "message": "Files uploaded successfully",
            "uploaded_files": uploaded_files
        }, status=status.HTTP_200_OK)
        
    except FileNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 