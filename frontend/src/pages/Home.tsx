import { Link } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useVoices } from '../hooks/useVoices';
import { useGenerations } from '../hooks/useGeneration';
import { useModels } from '../hooks/useModels';

export function Home() {
  const { voices, isLoading: isLoadingVoices } = useVoices();
  const { generations, isLoading: isLoadingGenerations } = useGenerations();
  const { backendInfo, isLoading: isLoadingModels } = useModels();

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          TTS Voice Cloning
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Clone your voice and generate natural-sounding speech with AI
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardBody className="text-center">
            <div className="text-4xl font-bold text-blue-600">
              {isLoadingVoices ? '...' : voices.length}
            </div>
            <p className="mt-2 text-gray-600">Voice Profiles</p>
            <Link to="/voices">
              <Button variant="text" size="sm" className="mt-3">
                View All →
              </Button>
            </Link>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <div className="text-4xl font-bold text-green-600">
              {isLoadingGenerations ? '...' : generations.length}
            </div>
            <p className="mt-2 text-gray-600">Generations</p>
            <Link to="/generate">
              <Button variant="text" size="sm" className="mt-3">
                Create New →
              </Button>
            </Link>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <div className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              {isLoadingModels ? '...' : backendInfo?.platform || 'Unknown'}
            </div>
            <p className="mt-2 text-gray-600">Backend Platform</p>
            <div className="mt-3 text-xs text-gray-500">
              {backendInfo?.current_model?.split('/').pop() || 'No model loaded'}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Getting Started */}
      <Card elevated>
        <CardBody className="space-y-6">
          <h2 className="text-2xl font-semibold text-gray-900">Getting Started</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Step 1 */}
            <div className="space-y-3">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900">1. Record Your Voice</h3>
              <p className="text-sm text-gray-600">
                Record a short voice sample (3-10 seconds) that will be used as reference for voice cloning.
              </p>
              <Link to="/voices">
                <Button variant="primary" size="sm">
                  Record Voice
                </Button>
              </Link>
            </div>

            {/* Step 2 */}
            <div className="space-y-3">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full">
                <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900">2. Transcribe (Automatic)</h3>
              <p className="text-sm text-gray-600">
                The system automatically transcribes your voice sample using Whisper AI.
              </p>
              <div className="text-xs text-gray-500 italic">
                Happens automatically after recording
              </div>
            </div>

            {/* Step 3 */}
            <div className="space-y-3">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full">
                <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900">3. Generate Speech</h3>
              <p className="text-sm text-gray-600">
                Enter any text and generate speech using your cloned voice.
              </p>
              <Link to="/generate">
                <Button variant="primary" size="sm">
                  Generate TTS
                </Button>
              </Link>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardBody className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 7H7v6h6V7z" />
                  <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Multi-Platform Support</h3>
                <p className="text-sm text-gray-600">
                  Works on Apple Silicon (MLX) and NVIDIA GPUs (PyTorch)
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">High Quality TTS</h3>
                <p className="text-sm text-gray-600">
                  Powered by Qwen3-TTS models (0.6B and 1.7B)
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
