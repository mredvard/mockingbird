import type { Generation } from '../../types';
import { GenerationCard } from './GenerationCard';

interface GenerationListProps {
  generations: Generation[];
  onDelete?: (generationId: string) => void;
  loading?: boolean;
  compact?: boolean;
}

export function GenerationList({ generations, onDelete, loading = false, compact = false }: GenerationListProps) {
  if (loading) {
    const gridClass = compact
      ? "space-y-3"
      : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";

    return (
      <div className={gridClass}>
        {[...Array(compact ? 3 : 6)].map((_, i) => (
          <div key={i} className="h-56 bg-gray-200 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (generations.length === 0) {
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
            d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No generations yet</h3>
        <p className="mt-1 text-sm text-gray-500">
          Generate your first TTS audio to see it here.
        </p>
      </div>
    );
  }

  const gridClass = compact
    ? "space-y-3"
    : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";

  return (
    <div className={gridClass}>
      {generations.map((generation) => (
        <GenerationCard
          key={generation.id}
          generation={generation}
          onDelete={() => onDelete?.(generation.id)}
        />
      ))}
    </div>
  );
}
