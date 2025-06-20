import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from audiobook.models import Novel, Character
from django.db import transaction
import uuid

class Command(BaseCommand):
    help = 'Import validated character personality data into database (only for existing novels)'

    def add_arguments(self, parser):
        parser.add_argument('--data_dir', type=str, default=None, help='Path to validated_character_personality_data (default: D:/FINAL_CODE/backend/ai_service/data/context_data/validated_character_personality_data)')

    def handle(self, *args, **options):
        data_dir = options['data_dir'] or r'D:/FINAL_CODE/backend/ai_service/data/context_data/validated_character_personality_data'
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {data_dir}'))
            return

        novel_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        imported_count = 0
        skipped_novel = 0
        skipped_character = 0
        for novel_id in novel_dirs:
            # Kiểm tra novel_id có phải UUID hợp lệ không
            try:
                uuid_obj = uuid.UUID(novel_id)
            except Exception:
                continue
            try:
                novel = Novel.objects.get(id=novel_id)
            except Novel.DoesNotExist:
                skipped_novel += 1
                continue
            novel_path = os.path.join(data_dir, novel_id)
            json_files = [f for f in os.listdir(novel_path) if f.endswith('.json')]
            for json_file in json_files:
                character_name = os.path.splitext(json_file)[0]
                json_path = os.path.join(novel_path, json_file)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # --- BẮT ĐẦU xử lý character_identity ---
                        ci = data.get("character_identity", {})
                        for field in ["name", "aliases", "raw_name", "confidence_score"]:
                            if field in ci:
                                ci.pop(field)
                        if "confirmed_identity" in ci and isinstance(ci["confirmed_identity"], list):
                            ci["confirmed_identity"] = ci["confirmed_identity"][0] if ci["confirmed_identity"] else None
                        data["character_identity"] = ci
                        # --- KẾT THÚC xử lý character_identity ---
                        character_info = json.dumps(data, ensure_ascii=False, indent=2)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error reading {json_path}: {str(e)}'))
                    continue
                # Tìm index tiếp theo cho character trong novel
                with transaction.atomic():
                    existing = Character.objects.filter(novel=novel, name=character_name, is_deleted=False).first()
                    if existing:
                        skipped_character += 1
                        continue
                    next_index = (Character.objects.filter(novel=novel).count() + 1)
                    Character.objects.create(
                        novel=novel,
                        name=character_name,
                        character_info=character_info,
                        index=next_index
                    )
                    imported_count += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {imported_count} characters. Skipped {skipped_novel} novels (not found), {skipped_character} characters (already exist).')) 