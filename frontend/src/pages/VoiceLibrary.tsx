import { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { VoiceRecorder } from '../components/voice/VoiceRecorder';
import { VoiceList } from '../components/voice/VoiceList';
import { useVoices } from '../hooks/useVoices';

export function VoiceLibrary() {
  const { voices, isLoading, createVoice, deleteVoice, isCreating } = useVoices();
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [voiceName, setVoiceName] = useState('');
  const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null);
  const [recordingDuration, setRecordingDuration] = useState(0);

  const handleRecordingComplete = (blob: Blob, duration: number) => {
    setRecordedAudio(blob);
    setRecordingDuration(duration);
  };

  const handleSaveVoice = async () => {
    if (!recordedAudio || !voiceName.trim()) {
      alert('Please record audio and enter a name');
      return;
    }

    try {
      await createVoice({
        audio: recordedAudio,
        name: voiceName.trim(),
        autoTranscribe: true,
      });

      // Reset and close
      setShowRecordModal(false);
      setVoiceName('');
      setRecordedAudio(null);
      setRecordingDuration(0);
    } catch (error) {
      console.error('Failed to create voice:', error);
      alert('Failed to save voice. Please try again.');
    }
  };

  const handleDeleteVoice = async (voiceId: string) => {
    try {
      await deleteVoice(voiceId);
    } catch (error) {
      console.error('Failed to delete voice:', error);
      alert('Failed to delete voice. Please try again.');
    }
  };

  const handleCloseModal = () => {
    setShowRecordModal(false);
    setVoiceName('');
    setRecordedAudio(null);
    setRecordingDuration(0);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Voice Library</h1>
          <p className="mt-2 text-gray-600">
            Manage your voice profiles for TTS generation
          </p>
        </div>
        <Button onClick={() => setShowRecordModal(true)} variant="primary" size="lg">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
          </svg>
          Record New Voice
        </Button>
      </div>

      {/* Voice List */}
      <VoiceList
        voices={voices}
        loading={isLoading}
        onDelete={handleDeleteVoice}
      />

      {/* Record Modal */}
      <Modal
        open={showRecordModal}
        onClose={handleCloseModal}
        title="Record Voice Sample"
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSaveVoice}
              disabled={!recordedAudio || !voiceName.trim() || isCreating}
              loading={isCreating}
            >
              Save Voice
            </Button>
          </>
        }
      >
        <div className="space-y-6">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div className="text-sm text-blue-800">
                <p className="font-medium">Tips for best results:</p>
                <ul className="mt-2 space-y-1 list-disc list-inside">
                  <li>Record 3-10 seconds of clear speech</li>
                  <li>Speak naturally in a quiet environment</li>
                  <li>Avoid background noise and echo</li>
                  <li>The audio will be automatically transcribed</li>
                </ul>
              </div>
            </div>
          </div>

          <Input
            label="Voice Name"
            placeholder="e.g., My Voice, Professional Tone"
            value={voiceName}
            onChange={(e) => setVoiceName(e.target.value)}
            helperText="Give your voice profile a memorable name"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Record Audio
            </label>
            <VoiceRecorder
              onRecordingComplete={handleRecordingComplete}
              maxDuration={60}
            />
          </div>

          {recordedAudio && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-green-800">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>
                  Recording complete ({recordingDuration.toFixed(1)}s). Enter a name and click "Save Voice".
                </span>
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}
