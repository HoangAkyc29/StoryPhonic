import os
import json
from django.core.management.base import BaseCommand
from audiobook.models import Voice

# Đường dẫn tuyệt đối tới hai thư mục chứa các file json
DIR_MAPPING = r'D:\FINAL_CODE\backend\ai_service\data\voice_data\reference_voice_data\character_personality_mapping'
DIR_MAPPING_BY_LORE = r'D:\FINAL_CODE\backend\ai_service\data\voice_data\reference_voice_data\character_personality_mapping_by_lore'

class Command(BaseCommand):
    help = 'Import and merge character personality mapping from two directories into Voice model.'

    def handle(self, *args, **options):
        # Lấy danh sách file json từ cả hai thư mục
        files_mapping = set(f for f in os.listdir(DIR_MAPPING) if f.endswith('.json'))
        files_mapping_by_lore = set(f for f in os.listdir(DIR_MAPPING_BY_LORE) if f.endswith('.json'))
        common_files = files_mapping & files_mapping_by_lore

        if not common_files:
            self.stdout.write(self.style.WARNING('No matching json files found in both directories.'))
            return

        for filename in common_files:
            path_mapping = os.path.join(DIR_MAPPING, filename)
            path_by_lore = os.path.join(DIR_MAPPING_BY_LORE, filename)
            try:
                with open(path_mapping, 'r', encoding='utf-8') as f1:
                    data_mapping = json.load(f1)
                with open(path_by_lore, 'r', encoding='utf-8') as f2:
                    data_by_lore = json.load(f2)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error reading {filename}: {e}'))
                continue

            # Tạo json tạm thời theo cấu trúc yêu cầu
            # character_identity
            char_info = data_by_lore.get('character_info', {})
            speaker_info = data_mapping.get('speaker_info', {})
            temp_json = {
                'character_identity': {
                    'confirmed_identity': char_info.get('name', ''),
                    'gender': char_info.get('gender', speaker_info.get('gender', '')),
                    'approximate_age': speaker_info.get('age', '')
                },
                'personality_traits': {},
                'core_personality_adjectives': data_by_lore.get('core_personality_adjectives', [])
            }
            # personality_traits (OCEAN)
            ocean = data_by_lore.get('OCEAN_assessment', {})
            temp_json['personality_traits'] = {
                'openness': ocean.get('Openness', {}).get('score'),
                'conscientiousness': ocean.get('Conscientiousness', {}).get('score'),
                'extraversion': ocean.get('Extraversion', {}).get('score'),
                'agreeableness': ocean.get('Agreeableness', {}).get('score'),
                'neuroticism': ocean.get('Neuroticism', {}).get('score'),
            }

            # Lưu vào Voice model
            voice_actor_name = char_info.get('name', None)
            if not voice_actor_name:
                self.stdout.write(self.style.ERROR(f'No character name in {filename}, skipping.'))
                continue
            # Tìm hoặc tạo mới Voice
            voice, created = Voice.objects.get_or_create(
                voice_actor_name=voice_actor_name,
                defaults={
                    'voice_actor_info': json.dumps(temp_json, ensure_ascii=False, indent=2)
                }
            )
            if not created:
                voice.voice_actor_info = json.dumps(temp_json, ensure_ascii=False, indent=2)
                voice.save()
            self.stdout.write(self.style.SUCCESS(f'Processed {filename} for {voice_actor_name}')) 