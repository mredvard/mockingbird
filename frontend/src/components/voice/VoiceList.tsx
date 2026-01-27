import type { Voice } from '../../types';
import { VoiceCard } from './VoiceCard';

interface VoiceListProps {
  voices: Voice[];
  selectedVoiceId?: string;
  onSelect?: (voice: Voice) => void;
  onDelete?: (voiceId: string) => void;
  loading?: boolean;
  compact?: boolean;
}

export function VoiceList({
  voices,
  selectedVoiceId,
  onSelect,
  onDelete,
  loading = false,
  compact = false,
}: VoiceListProps) {
  if (loading) {
    const gridClass = compact
      ? "grid grid-cols-1 gap-4"
      : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";

    return (
      <div className={gridClass}>
        {[...Array(compact ? 3 : 6)].map((_, i) => (
          <div
            key={i}
            className="h-48 bg-gray-200 rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (voices.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No voice samples</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by recording a voice sample.
        </p>
      </div>
    );
  }

  const gridClass = compact
    ? "grid grid-cols-1 gap-4"
    : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";

  return (
    <div className={gridClass}>
      {voices.map((voice) => (
        <VoiceCard
          key={voice.id}
          voice={voice}
          selected={voice.id === selectedVoiceId}
          onSelect={() => onSelect?.(voice)}
          onDelete={() => onDelete?.(voice.id)}
        />
      ))}
    </div>
  );
}
