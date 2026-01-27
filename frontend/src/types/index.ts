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

// API error response
export interface ApiError {
  detail: string;
}
