import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { generationApi } from '../services/api';
import type { GenerationRequest, Generation } from '../types';
import { useState, useEffect, useRef } from 'react';

export function useGenerations(voiceId?: string) {
  const queryClient = useQueryClient();

  const { data: generations = [], isLoading, error, refetch } = useQuery({
    queryKey: ['generations', voiceId],
    queryFn: () => generationApi.list(voiceId),
  });

  const deleteGeneration = useMutation({
    mutationFn: generationApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generations'] });
    },
  });

  return {
    generations,
    isLoading,
    error,
    refetch,
    deleteGeneration: deleteGeneration.mutateAsync,
    isDeleting: deleteGeneration.isPending,
  };
}

export function useGeneration(id: string | undefined) {
  const { data: generation, isLoading, error } = useQuery<Generation>({
    queryKey: ['generations', id],
    queryFn: () => generationApi.get(id!),
    enabled: !!id,
  });

  return { generation, isLoading, error };
}

// Hook for synchronous generation
export function useSyncGeneration() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (request: GenerationRequest) => generationApi.create(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generations'] });
    },
  });

  return {
    generate: mutation.mutateAsync,
    isGenerating: mutation.isPending,
    error: mutation.error,
  };
}

// Hook for asynchronous generation with progress tracking
export function useAsyncGeneration() {
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string>('idle');
  const [message, setMessage] = useState<string>('');
  const [result, setResult] = useState<Generation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollIntervalRef = useRef<number | null>(null);

  const startGeneration = async (request: GenerationRequest) => {
    try {
      setProgress(0);
      setStatus('starting');
      setMessage('Initializing...');
      setError(null);
      setResult(null);

      // Start async generation
      const taskResponse = await generationApi.createAsync(request);
      setStatus('polling');

      // Poll for progress
      pollIntervalRef.current = window.setInterval(async () => {
        try {
          const taskStatus = await generationApi.getTaskStatus(taskResponse.task_id);

          setProgress(taskStatus.progress);
          setStatus(taskStatus.status);
          setMessage(taskStatus.message);

          if (taskStatus.status === 'completed') {
            setResult(taskStatus.result || null);
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            // Clean up task
            await generationApi.deleteTask(taskResponse.task_id);
            // Invalidate queries
            queryClient.invalidateQueries({ queryKey: ['generations'] });
          } else if (taskStatus.status === 'failed') {
            setError(taskStatus.error || 'Generation failed');
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            // Clean up task
            await generationApi.deleteTask(taskResponse.task_id);
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to check status');
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        }
      }, 1000); // Poll every second
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start generation');
      setStatus('failed');
    }
  };

  const reset = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setProgress(0);
    setStatus('idle');
    setMessage('');
    setResult(null);
    setError(null);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  return {
    generate: startGeneration,
    progress,
    status,
    message,
    result,
    error,
    isGenerating: status !== 'idle' && status !== 'completed' && status !== 'failed',
    reset,
  };
}
