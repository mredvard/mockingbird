import { Textarea } from '../ui/Input';

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  maxLength?: number;
  placeholder?: string;
}

export function TextInput({ value, onChange, maxLength = 1000, placeholder }: TextInputProps) {
  const charCount = value.length;
  const isNearLimit = charCount > maxLength * 0.8;
  const isOverLimit = charCount > maxLength;

  return (
    <div className="space-y-2">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || 'Enter the text you want to convert to speech...'}
        rows={6}
        maxLength={maxLength}
        className="font-mono"
      />
      <div className="flex items-center justify-between text-sm">
        <p className="text-gray-500">
          Enter the text to generate speech with your selected voice
        </p>
        <span
          className={`font-medium ${
            isOverLimit
              ? 'text-red-600'
              : isNearLimit
              ? 'text-yellow-600'
              : 'text-gray-500'
          }`}
        >
          {charCount} / {maxLength}
        </span>
      </div>
    </div>
  );
}
