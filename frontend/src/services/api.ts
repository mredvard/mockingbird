import type {
  Voice,
  VoiceWithTranscription,
  Generation,
  GenerationRequest,
  GenerationTaskResponse,
  TaskStatus,
  BackendInfo,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || response.statusText);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Voice API
export const voiceApi = {
  async list(): Promise<Voice[]> {
    const response = await fetch(`${API_BASE}/api/voices`);
    return handleResponse(response);
  },

  async get(id: string): Promise<VoiceWithTranscription> {
    const response = await fetch(`${API_BASE}/api/voices/${id}`);
    return handleResponse(response);
  },

  async create(formData: FormData): Promise<Voice> {
    const response = await fetch(`${API_BASE}/api/voices`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(response);
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/voices/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  async transcribe(id: string): Promise<Voice> {
    const response = await fetch(`${API_BASE}/api/voices/${id}/transcribe`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  async updateTranscription(id: string, transcription: string): Promise<Voice> {
    const response = await fetch(`${API_BASE}/api/voices/${id}/transcription`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ transcription }),
    });
    return handleResponse(response);
  },

  getAudioUrl(id: string): string {
    return `${API_BASE}/api/voices/${id}/audio`;
  },
};

// Generation API
export const generationApi = {
  async list(voiceId?: string): Promise<Generation[]> {
    const params = new URLSearchParams();
    if (voiceId) params.append('voice_id', voiceId);

    const url = `${API_BASE}/api/generations${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async get(id: string): Promise<Generation> {
    const response = await fetch(`${API_BASE}/api/generations/${id}`);
    return handleResponse(response);
  },

  async create(request: GenerationRequest): Promise<Generation> {
    const response = await fetch(`${API_BASE}/api/generations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async createAsync(request: GenerationRequest): Promise<GenerationTaskResponse> {
    const response = await fetch(`${API_BASE}/api/generations/async`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await fetch(`${API_BASE}/api/generations/tasks/${taskId}`);
    return handleResponse(response);
  },

  async deleteTask(taskId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/generations/tasks/${taskId}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/generations/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  getAudioUrl(id: string): string {
    return `${API_BASE}/api/generations/${id}/audio`;
  },
};

// Models API
export const modelsApi = {
  async getInfo(): Promise<BackendInfo> {
    const response = await fetch(`${API_BASE}/api/generations/models/info`);
    return handleResponse(response);
  },

  async list(): Promise<string[]> {
    const response = await fetch(`${API_BASE}/api/generations/models/list`);
    return handleResponse(response);
  },
};

// Health check
export const healthApi = {
  async check() {
    const response = await fetch(`${API_BASE}/api/health`);
    return handleResponse(response);
  },
};

export { ApiError };
