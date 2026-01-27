import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { voiceApi } from '../services/api';
import type { Voice, VoiceWithTranscription } from '../types';

export function useVoices() {
  const queryClient = useQueryClient();

  const { data: voices = [], isLoading, error, refetch } = useQuery({
    queryKey: ['voices'],
    queryFn: voiceApi.list,
  });

  const createVoice = useMutation({
    mutationFn: async ({ audio, name, autoTranscribe = true }: {
      audio: Blob;
      name: string;
      autoTranscribe?: boolean;
    }) => {
      const formData = new FormData();
      formData.append('audio', audio, 'recording.webm');
      formData.append('name', name);
      formData.append('auto_transcribe', String(autoTranscribe));
      return voiceApi.create(formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voices'] });
    },
  });

  const deleteVoice = useMutation({
    mutationFn: voiceApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voices'] });
    },
  });

  const transcribeVoice = useMutation({
    mutationFn: voiceApi.transcribe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voices'] });
    },
  });

  const updateTranscription = useMutation({
    mutationFn: ({ id, transcription }: { id: string; transcription: string }) =>
      voiceApi.updateTranscription(id, transcription),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voices'] });
    },
  });

  return {
    voices,
    isLoading,
    error,
    refetch,
    createVoice: createVoice.mutateAsync,
    deleteVoice: deleteVoice.mutateAsync,
    transcribeVoice: transcribeVoice.mutateAsync,
    updateTranscription: updateTranscription.mutateAsync,
    isCreating: createVoice.isPending,
    isDeleting: deleteVoice.isPending,
    isTranscribing: transcribeVoice.isPending,
  };
}

export function useVoice(id: string | undefined) {
  const { data: voice, isLoading, error } = useQuery<VoiceWithTranscription>({
    queryKey: ['voices', id],
    queryFn: () => voiceApi.get(id!),
    enabled: !!id,
  });

  return { voice, isLoading, error };
}
