import { Select } from '../ui/Select';

interface ModelSelectorProps {
  models: string[];
  selected: string;
  onChange: (model: string) => void;
  disabled?: boolean;
}

export function ModelSelector({ models, selected, onChange, disabled = false }: ModelSelectorProps) {
  const options = models.map((model) => ({
    value: model,
    label: formatModelName(model),
  }));

  function formatModelName(model: string): string {
    // Extract model size from name (e.g., "0.6B" or "1.7B")
    const sizeMatch = model.match(/(\d+\.?\d*)B/);
    const size = sizeMatch ? sizeMatch[1] : '';

    if (model.includes('mlx-community')) {
      return `MLX - Qwen3 TTS ${size}B`;
    } else if (model.includes('Qwen')) {
      return `PyTorch - Qwen3 TTS ${size}B`;
    }

    return model;
  }

  return (
    <div className="space-y-2">
      <Select
        label="TTS Model"
        options={options}
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        helperText="Select the AI model to use for generation"
      />

      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-blue-800">
            <p className="font-medium">Model Info:</p>
            <ul className="mt-1 space-y-1 list-disc list-inside">
              <li>1.7B models provide better quality but are slower</li>
              <li>0.6B models are faster but may have lower quality</li>
              <li>First generation will download the model (~1.5-3.5GB)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
