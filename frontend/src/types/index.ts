// Voice types
export interface Voice {
  id: string;
  name: string;
  created_at: string;
  has_transcription: boolean;
  duration?: number;
}

export interface VoiceWithTranscription extends Voice {
  transcription?: string;
}

export interface VoiceCreate {
  name: string;
}

// Generation types
export interface Generation {
  id: string;
  text: string;
  voice_id: string;
  model: string;
  created_at: string;
  duration?: number;
  audio_url: string;
}

export interface GenerationRequest {
  text: string;
  voice_id: string;
  model?: string;
}

// Backend info
export interface BackendInfo {
  platform: string;
  current_model?: string;
  available_models: string[];
  sample_rate: number;
}

// Task and progress types
export interface TaskStatus {
  id: string;
  status: 'pending' | 'initializing' | 'generating' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  message: string;
  created_at: string;
  updated_at: string;
  result?: Generation | null;
  error?: string | null;
}

export interface GenerationTaskResponse {
  task_id: string;
  message: string;
  status_url: string;
}

// API error response
export interface ApiError {
  detail: string;
}
