from django.core.management.base import BaseCommand
from audiobook.services.context_data_service import process_context_data

class Command(BaseCommand):
    help = 'Process context data for a novel'

    def add_arguments(self, parser):
        parser.add_argument('novel_id', type=str, help='ID of the novel to process')

    def handle(self, *args, **options):
        novel_id = options['novel_id']
        self.stdout.write(f'Processing context data for novel {novel_id}...')
        
        success = process_context_data(novel_id)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'Successfully processed context data for novel {novel_id}'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to process context data for novel {novel_id}')) 