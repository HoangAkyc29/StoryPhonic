export interface Novel {
  id: string
  user: string
  name: string
  content: string
  status: string
  created_at: string
  s3_audio_metadata_url: string | null
  s3_audio_file_url: string | null
  is_deleted: boolean
}

export interface CreateNovelData {
  name: string
  content?: string
  content_file?: File
}

export interface Character {
  id: string
  novel: string
  name: string
  character_info: string
  index: number
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface TextChunk {
  id: string
  novel: string
  content: string
  index: number
  status: string
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface ChunkAnnotation {
  id: string
  novel: string
  raw_text: string
  clean_text: string
  index: number
  status: string
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface ChunkContextMemory {
  id: string
  novel: string
  content: string
  index: number
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface SentenceAnnotation {
  id: string
  novel: string
  context: string
  index: number
  type: string
  raw_character: string
  emotion: string
  identity: string | null
  gender: 'Male' | 'Female'
  voice_actor: string
  chunk_annotation_belong: string | null
  chunk_index: number
  created_at: string
  updated_at: string
  is_deleted: boolean
} 