import { useState } from 'react';
import type { Voice } from '../../types';
import { Card, CardBody, CardFooter } from '../ui/Card';
import { Button } from '../ui/Button';
import { AudioPlayer } from '../ui/AudioPlayer';
import { voiceApi } from '../../services/api';
import { useVoice } from '../../hooks/useVoices';

interface VoiceCardProps {
  voice: Voice;
  onSelect?: () => void;
  onDelete?: () => void;
  onViewTranscription?: () => void;
  selected?: boolean;
}

export function VoiceCard({ voice, onSelect, onDelete, onViewTranscription, selected = false }: VoiceCardProps) {
  const [showTranscription, setShowTranscription] = useState(false);
  const { voice: voiceDetail } = useVoice(showTranscription ? voice.id : undefined);
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${voice.name}"?`)) {
      onDelete?.();
    }
  };

  return (
    <Card
      elevated={selected}
      className={`transition-all ${selected ? 'ring-2 ring-blue-500' : 'hover:shadow-md'}`}
    >
      <CardBody className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{voice.name}</h3>
            <p className="text-sm text-gray-500">{formatDate(voice.created_at)}</p>
          </div>
          {selected && (
            <span className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full">
              Selected
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          {voice.has_transcription ? (
            <span className="text-green-600">Transcribed</span>
          ) : (
            <span className="text-gray-400">No transcription</span>
          )}
        </div>

        {voice.duration && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <span>{voice.duration.toFixed(1)}s</span>
          </div>
        )}

        <AudioPlayer src={voiceApi.getAudioUrl(voice.id)} />

        {/* Transcription Section */}
        {voice.has_transcription && (
          <div className="mt-3 border-t pt-3">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowTranscription(!showTranscription);
              }}
              className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
            >
              <svg
                className={`w-4 h-4 transition-transform ${showTranscription ? 'rotate-90' : ''}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              <span>Transcription</span>
            </button>

            {showTranscription && voiceDetail?.transcription && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {voiceDetail.transcription}
                </p>
              </div>
            )}

            {showTranscription && !voiceDetail?.transcription && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500 italic">Loading transcription...</p>
              </div>
            )}
          </div>
        )}
      </CardBody>

      <CardFooter className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {voice.has_transcription && onViewTranscription && (
            <Button
              variant="text"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onViewTranscription();
              }}
              className="text-blue-600 hover:bg-blue-50"
            >
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
              </svg>
              View Transcription
            </Button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {onSelect && (
            <Button
              variant={selected ? 'secondary' : 'primary'}
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onSelect();
              }}
            >
              {selected ? 'Selected' : 'Use This Voice'}
            </Button>
          )}
          {onDelete && (
            <Button
              variant="text"
              size="sm"
              onClick={handleDelete}
              className="text-red-600 hover:bg-red-50"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
