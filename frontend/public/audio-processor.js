class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.frameSize = 1024;
    this.sampleCount = 0;
    this.buffer = new Float32Array(this.frameSize);
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];
    
    if (input.length > 0) {
      const inputChannel = input[0];
      
      // Fill buffer with incoming audio
      for (let i = 0; i < inputChannel.length; i++) {
        this.buffer[this.sampleCount] = inputChannel[i];
        this.sampleCount++;
        
        // When buffer is full, send it to main thread
        if (this.sampleCount >= this.frameSize) {
          // Convert Float32 to Int16 PCM
          const pcmData = new Int16Array(this.frameSize);
          for (let j = 0; j < this.frameSize; j++) {
            const sample = Math.max(-1, Math.min(1, this.buffer[j]));
            pcmData[j] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
          }
          
          // Send audio frame to main thread
          this.port.postMessage({
            type: 'audio_frame',
            data: pcmData.buffer
          });
          
          // Reset buffer
          this.sampleCount = 0;
        }
      }
    }
    
    // Pass through audio to output (optional)
    if (output.length > 0) {
      const outputChannel = output[0];
      for (let i = 0; i < outputChannel.length; i++) {
        outputChannel[i] = input[0]?.[i] || 0;
      }
    }
    
    return true;
  }
}

registerProcessor('audio-processor', AudioProcessor);
