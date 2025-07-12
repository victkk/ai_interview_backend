/**
 * AudioRecorderProcessor
 * This class runs in a separate AudioWorkletGlobalScope.
 * Its purpose is to receive raw audio data (Float32Array), convert it to 16-bit PCM,
 * and post it back to the main thread.
 */
class AudioRecorderProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    /**
     * This method is called for every block of audio data processed by the audio graph.
     * @param {Float32Array[][]} inputs - An array of inputs, each with an array of channels.
     * @param {Float32Array[][]} outputs - An array of outputs (we don't use this).
     * @param {Record<string, Float32Array>} parameters - Audio parameters (we don't use this).
     * @returns {boolean} - Return true to keep the processor alive.
     */
    process(inputs, outputs, parameters) {
        // We only use the first input, and the first channel of that input.
        const channelData = inputs[0][0];
        
        // The channelData is a Float32Array. We need to convert it to 16-bit PCM.
        if (channelData) {
            const buffer = new Int16Array(channelData.length);
            for (let i = 0; i < channelData.length; i++) {
                // Clamp values to the [-1, 1] range and scale to the 16-bit integer range.
                buffer[i] = Math.max(-1, Math.min(1, channelData[i])) * 32767;
            }
            // Post the raw PCM data (as a transferable ArrayBuffer) back to the main thread.
            this.port.postMessage(buffer.buffer, [buffer.buffer]);
        }
        
        // Return true to keep the processor alive.
        return true;
    }
}

// Register the processor, making it available for use in the AudioWorkletNode.
registerProcessor('audio-recorder-processor', AudioRecorderProcessor);
