import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, CardBody, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { TextInput } from '../components/generation/TextInput';
import { ModelSelector } from '../components/generation/ModelSelector';
import { VoiceList } from '../components/voice/VoiceList';
import { GenerationList } from '../components/generation/GenerationList';
import { useVoices } from '../hooks/useVoices';
import { useGenerations, useAsyncGeneration } from '../hooks/useGeneration';
import { useModels } from '../hooks/useModels';
import type { Voice } from '../types';

export function Generate() {
  const location = useLocation();
  const { voices, isLoading: isLoadingVoices, deleteVoice } = useVoices();
  const { generations, deleteGeneration } = useGenerations();
  const { models, currentModel } = useModels();
  const {
    generate,
    progress,
    status,
    message,
    result,
    error: genError,
    isGenerating,
    reset,
  } = useAsyncGeneration();

  const [selectedVoice, setSelectedVoice] = useState<Voice | null>(null);
  const [text, setText] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('');

  // Set voice from navigation state if provided
  useEffect(() => {
    const state = location.state as { selectedVoice?: Voice };
    if (state?.selectedVoice) {
      setSelectedVoice(state.selectedVoice);
      // Clear the state after using it
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  // Set default model when available
  useEffect(() => {
    if (models.length > 0 && !selectedModel) {
      setSelectedModel(currentModel || models[0]);
    }
  }, [models, currentModel, selectedModel]);

  // Reset when generation completes
  useEffect(() => {
    if (result) {
      // Clear form after successful generation
      setText('');
      // Reset after showing result briefly
      setTimeout(() => {
        reset();
      }, 3000);
    }
  }, [result, reset]);

  const handleGenerate = async () => {
    if (!selectedVoice) {
      alert('Please select a voice profile');
      return;
    }

    if (!text.trim()) {
      alert('Please enter text to generate');
      return;
    }

    if (!selectedModel) {
      alert('Please select a model');
      return;
    }

    try {
      await generate({
        text: text.trim(),
        voice_id: selectedVoice.id,
        model: selectedModel,
      });
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  const handleDeleteGeneration = async (id: string) => {
    try {
      await deleteGeneration(id);
    } catch (error) {
      console.error('Failed to delete generation:', error);
      alert('Failed to delete generation. Please try again.');
    }
  };

  const handleDeleteVoice = async (id: string) => {
    try {
      await deleteVoice(id);
      // Clear selection if the deleted voice was selected
      if (selectedVoice?.id === id) {
        setSelectedVoice(null);
      }
    } catch (error) {
      console.error('Failed to delete voice:', error);
      alert('Failed to delete voice. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Generate TTS</h1>
        <p className="mt-2 text-gray-600">
          Create speech from text using your voice profiles
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Generation Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Voice Selection */}
          <Card elevated>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">Select Voice</h2>
            </CardHeader>
            <CardBody>
              {voices.length === 0 && !isLoadingVoices ? (
                <div className="text-center py-8">
                  <p className="text-gray-600">No voice profiles available.</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Please record a voice sample first.
                  </p>
                </div>
              ) : (
                <VoiceList
                  voices={voices}
                  loading={isLoadingVoices}
                  selectedVoiceId={selectedVoice?.id}
                  onSelect={setSelectedVoice}
                  onDelete={handleDeleteVoice}
                  compact={true}
                />
              )}
            </CardBody>
          </Card>

          {/* Text Input */}
          <Card elevated>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">Enter Text</h2>
            </CardHeader>
            <CardBody>
              <TextInput
                value={text}
                onChange={setText}
                maxLength={1000}
              />
            </CardBody>
          </Card>

          {/* Model Selection */}
          <Card elevated>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">Model Settings</h2>
            </CardHeader>
            <CardBody>
              <ModelSelector
                models={models}
                selected={selectedModel}
                onChange={setSelectedModel}
                disabled={isGenerating}
              />
            </CardBody>
          </Card>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            variant="primary"
            size="lg"
            disabled={isGenerating || !selectedVoice || !text.trim()}
            loading={isGenerating}
            className="w-full"
          >
            {isGenerating ? 'Generating...' : 'Generate Speech'}
          </Button>

          {/* Progress Display */}
          {isGenerating && (
            <Card elevated className="border-blue-300">
              <CardBody className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">Generating...</h3>
                  <span className="text-sm font-medium text-blue-600">{progress}%</span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <p className="text-sm text-gray-600">{message}</p>

                {status === 'generating' && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      This may take 1-3 minutes. Please wait...
                    </p>
                  </div>
                )}
              </CardBody>
            </Card>
          )}

          {/* Success Message */}
          {result && (
            <Card elevated className="border-green-300">
              <CardBody>
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-green-900">Generation Complete!</h3>
                    <p className="text-sm text-green-700 mt-1">
                      Your audio has been generated successfully. Check the history below to play it.
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Error Message */}
          {genError && (
            <Card elevated className="border-red-300">
              <CardBody>
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-red-900">Generation Failed</h3>
                    <p className="text-sm text-red-700 mt-1">{genError}</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}
        </div>

        {/* Sidebar - Generation History */}
        <div className="lg:col-span-1">
          <Card elevated className="sticky top-6">
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">Recent Generations</h2>
            </CardHeader>
            <CardBody className="max-h-[calc(100vh-200px)] overflow-y-auto">
              <GenerationList
                generations={generations.slice(0, 10)}
                onDelete={handleDeleteGeneration}
                compact={true}
              />
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
