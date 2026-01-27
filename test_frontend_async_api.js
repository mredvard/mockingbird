/**
 * Simple test script to verify the async generation API endpoints
 * Run with: node test_frontend_async_api.js
 */

const API_BASE = 'http://localhost:8000';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testAsyncGeneration() {
  console.log('🧪 Testing Frontend Async Generation API Integration\n');

  try {
    // 1. Get list of voices
    console.log('1️⃣ Fetching voices...');
    const voicesResponse = await fetch(`${API_BASE}/api/voices`);
    const voices = await voicesResponse.json();
    console.log(`   ✅ Found ${voices.length} voice(s)`);

    if (voices.length === 0) {
      console.log('   ⚠️  No voices available. Please create a voice first.');
      return;
    }

    const voice = voices[0];
    console.log(`   📢 Using voice: ${voice.name} (${voice.id})\n`);

    // 2. Start async generation
    console.log('2️⃣ Starting async generation...');
    const generateResponse = await fetch(`${API_BASE}/api/generations/async`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Hola, esta es una prueba de generación asíncrona.',
        voice_id: voice.id,
      }),
    });

    if (!generateResponse.ok) {
      const error = await generateResponse.json();
      throw new Error(`Generation failed: ${error.detail}`);
    }

    const taskResponse = await generateResponse.json();
    console.log(`   ✅ Task started: ${taskResponse.task_id}`);
    console.log(`   📍 Status URL: ${taskResponse.status_url}\n`);

    // 3. Poll for progress
    console.log('3️⃣ Polling for progress...');
    let status;
    let lastProgress = -1;

    while (true) {
      const statusResponse = await fetch(`${API_BASE}${taskResponse.status_url}`);
      status = await statusResponse.json();

      // Only log if progress changed
      if (status.progress !== lastProgress) {
        const progressBar = '█'.repeat(Math.floor(status.progress / 5)) + '░'.repeat(20 - Math.floor(status.progress / 5));
        console.log(`   [${progressBar}] ${status.progress}% - ${status.status}: ${status.message}`);
        lastProgress = status.progress;
      }

      if (status.status === 'completed') {
        console.log(`   ✅ Generation completed!\n`);
        break;
      }

      if (status.status === 'failed') {
        throw new Error(`Generation failed: ${status.error}`);
      }

      await sleep(1000); // Poll every second
    }

    // 4. Display results
    console.log('4️⃣ Results:');
    console.log(`   📝 Text: ${status.result.text}`);
    console.log(`   🎵 Voice: ${status.result.voice_id}`);
    console.log(`   🤖 Model: ${status.result.model}`);
    console.log(`   🔗 Audio URL: ${API_BASE}${status.result.audio_url}`);
    console.log(`   ⏱️  Duration: ${status.result.duration?.toFixed(2) || 'N/A'}s`);
    console.log(`   🕐 Created: ${status.result.created_at}\n`);

    // 5. Clean up task
    console.log('5️⃣ Cleaning up task...');
    await fetch(`${API_BASE}/api/generations/tasks/${taskResponse.task_id}`, {
      method: 'DELETE',
    });
    console.log('   ✅ Task removed from tracking\n');

    console.log('✅ All tests passed! Frontend API integration is working correctly.\n');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
testAsyncGeneration();
