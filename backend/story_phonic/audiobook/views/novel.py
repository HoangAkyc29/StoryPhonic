from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models.novel import Novel
from ..serializers.novel import NovelSerializer
from ..permissions import IsOwnerOrAdmin
from ..utils import save_novel_file, read_file_content

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

    def perform_destroy(self, instance):
        # Soft delete novel và toàn bộ object con
        instance.is_deleted = True
        instance.save()
        # Soft delete các object con
        for rel in ['text_chunks', 'chunk_context_memories', 'chunk_annotations', 'characters', 'sentence_annotations']:
            for obj in getattr(instance, rel).all():
                obj.is_deleted = True
                obj.save() 