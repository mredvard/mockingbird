import type { Generation } from '../../types';
import { Card, CardBody, CardFooter } from '../ui/Card';
import { Button } from '../ui/Button';
import { AudioPlayer } from '../ui/AudioPlayer';

interface GenerationCardProps {
  generation: Generation;
  onDelete?: () => void;
}

export function GenerationCard({ generation, onDelete }: GenerationCardProps) {
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

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = generation.audio_url;
    link.download = `generation-${generation.id}.wav`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this generation?')) {
      onDelete?.();
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardBody className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 line-clamp-2">
              {generation.text}
            </p>
            <p className="text-xs text-gray-500 mt-1">{formatDate(generation.created_at)}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 text-xs">
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full">
            {generation.model.includes('0.6B') ? '0.6B' : generation.model.includes('1.7B') ? '1.7B' : 'Model'}
          </span>
          {generation.duration && (
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
              {generation.duration.toFixed(1)}s
            </span>
          )}
        </div>

        <AudioPlayer src={generation.audio_url} />
      </CardBody>

      <CardFooter className="flex items-center justify-end gap-2">
        <Button variant="secondary" size="sm" onClick={handleDownload}>
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          Download
        </Button>
        {onDelete && (
          <Button variant="text" size="sm" onClick={handleDelete} className="text-red-600 hover:bg-red-50">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
