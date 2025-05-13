from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from audiobook.models.novel import Novel
from audiobook.serializers.novel import NovelSerializer
from audiobook.permissions import IsOwnerOrAdmin
from audiobook.utils import save_novel_file, read_file_content
from audiobook.tasks import thread_create_audiobook
import threading

class NovelViewSet(viewsets.ModelViewSet):
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Novel.objects.filter(is_deleted=False)
        if hasattr(user, 'roles') and user.roles.filter(name='admin').exists():
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        # Save the novel first to get its ID
        novel = serializer.save(user=self.request.user)
        
        # Handle file upload if present
        content_file = self.request.FILES.get('content_file')
        file_path = None
        if content_file:
            try:
                # Save the file
                file_path = save_novel_file(novel.id, content_file)
                
                # Read content from file if it's a text file
                if content_file.name.lower().endswith('.txt'):
                    content = read_file_content(file_path)
                    novel.content = content
                    novel.save()
            except Exception as e:
                # If there's an error, delete the novel and raise the error
                novel.delete()
                raise e

        # Start the audiobook creation thread
        thread = threading.Thread(
            target=thread_create_audiobook,
            args=(novel, file_path)
        )
        thread.start()

    def perform_destroy(self, instance):
        # Soft delete novel và toàn bộ object con
        instance.is_deleted = True
        instance.save()
        # Soft delete các object con
        for rel in ['text_chunks', 'chunk_context_memories', 'chunk_annotations', 'characters', 'sentence_annotations']:
            for obj in getattr(instance, rel).all():
                obj.is_deleted = True
                obj.save()

    @action(detail=True, methods=['post'])
    def create_audiobook(self, request, pk=None):
        """API endpoint to manually trigger audiobook creation"""
        novel = self.get_object()
        
        # Check if novel is already being processed
        if novel.status in ['pending', 'running']:
            return Response(
                {"error": "Novel is already being processed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to running
        novel.status = 'running'
        novel.save()
        
        # Start the audiobook creation thread
        thread = threading.Thread(
            target=thread_create_audiobook,
            args=(novel, None)
        )
        thread.start()
        
        return Response(
            {"message": "Audiobook creation started", "novel_id": str(novel.id)},
            status=status.HTTP_202_ACCEPTED
        ) 