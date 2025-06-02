import os
from django.core.management.base import BaseCommand
from django.conf import settings
from audiobook.models import Novel
import shutil
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Delete all data related to deleted novels'

    def handle(self, *args, **options):
        # Get all deleted novel IDs
        deleted_novel_ids = Novel.objects.filter(is_deleted=1).values_list('id', flat=True)
        
        if not deleted_novel_ids:
            self.stdout.write(self.style.SUCCESS('No deleted novels found'))
            return

        # Load environment variables from .env file
        load_dotenv()
        data_dir = os.getenv('DATA_DIR_ABSOLUTE')
        
        if not data_dir:
            self.stdout.write(self.style.ERROR('DATA_DIR_ABSOLUTE not found in .env file'))
            return

        # Directories to check
        directories_to_check = [
            os.path.join(data_dir, 'context_data', 'validated_character_personality_data'),
            os.path.join(data_dir, 'context_data', 'character_label_data'),
            os.path.join(data_dir, 'context_data', 'character_personality_data'),
            os.path.join(data_dir, 'context_data', 'context_memory_data'),
            os.path.join(data_dir, 'context_data', 'text_input_data'),
            os.path.join(data_dir, 'context_data', 'input_data_directory'),
            os.path.join(data_dir, 'context_data', 'personality_mapper_data'),
            os.path.join(data_dir, 'context_data', 'personality_mapper_data', 'mapped_character-VA'),
            os.path.join(data_dir, 'voice_data', 'temporary_output_voice_data', 'text_to_speech'),
            os.path.join(data_dir, 'voice_data', 'temporary_output_voice_data', 'voice_conversion'),
            os.path.join(data_dir, 'voice_data', 'temporary_output_voice_data', 'final_audio_output')
        ]

        deleted_count = 0
        for novel_id in deleted_novel_ids:
            novel_id_str = str(novel_id)
            
            for directory in directories_to_check:
                if not os.path.exists(directory):
                    continue

                # Check for directories matching the novel ID
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    
                    # If it's a directory and matches the novel ID
                    if os.path.isdir(item_path) and item == novel_id_str:
                        try:
                            shutil.rmtree(item_path)
                            self.stdout.write(f'Deleted directory: {item_path}')
                            deleted_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error deleting directory {item_path}: {str(e)}'))
                    
                    # If it's a file, check if the name (before extension) matches the novel ID
                    elif os.path.isfile(item_path):
                        file_name = os.path.splitext(item)[0]
                        if file_name == novel_id_str:
                            try:
                                os.remove(item_path)
                                self.stdout.write(f'Deleted file: {item_path}')
                                deleted_count += 1
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'Error deleting file {item_path}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} items')) 