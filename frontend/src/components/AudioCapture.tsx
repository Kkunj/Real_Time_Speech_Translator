import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Mic, MicOff, Monitor, Square } from 'lucide-react'
import { ConnectionState, LanguagePair, TranscriptEntry } from '../types'
import { getWebSocketUrl } from '../config/env'

interface AudioCaptureProps {
  onConnectionChange: (state: ConnectionState) => void
  onTranscriptUpdate: (entry: TranscriptEntry) => void
  onSessionStart: (sessionId: string) => void
  languagePair: LanguagePair
  connectionState: ConnectionState
}

const AudioCapture: React.FC<AudioCaptureProps> = ({
  onConnectionChange,
  onTranscriptUpdate,
  onSessionStart,
  languagePair,
  connectionState
}) => {
  const [isCapturing, setIsCapturing] = useState(false)
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false)
  const [error, setError] = useState<string>('')
  const [audioLevel, setAudioLevel] = useState<number>(0)
  const [isRecording, setIsRecording] = useState(false)
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string>('')
  
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<AudioWorkletNode | ScriptProcessorNode | null>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const sessionIdRef = useRef<string>('')
  const audioLevelIntervalRef = useRef<number | null>(null)
  const testAudioIntervalRef = useRef<number | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const frameBufferRef = useRef<Float32Array[]>([])
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recordedChunksRef = useRef<Blob[]>([])
  
  // Audio configuration for AssemblyAI
  const SAMPLE_RATE = 16000
  const FRAME_SIZE = 2048 // 128ms at 16kHz (16000 * 0.128 = 2048 samples) - power of 2
  const CHANNELS = 1

  const generateSessionId = useCallback(() => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }, [])

    const connectWebSocket = useCallback(async () => {
    return new Promise((resolve, reject) => {
      try {
        onConnectionChange('connecting')
        setIsWebSocketConnected(false)
        
        // Use environment configuration for WebSocket URL (Render deployment)
        const wsUrl = getWebSocketUrl()
        console.log('Connecting to WebSocket:', wsUrl)
        
        const ws = new WebSocket(wsUrl)
        
        ws.onopen = () => {
          console.log('WebSocket connected successfully (Azure Speech)')
          onConnectionChange('connected')
          setIsWebSocketConnected(true)
          
          websocketRef.current = ws
          
          // Send Azure-specific init message
          try {
            const sessionId = generateSessionId()
            sessionIdRef.current = sessionId
            onSessionStart(sessionId)
            
            console.log('Sending Azure Speech init_session message...')
            ws.send(JSON.stringify({
              type: 'session_init',
              sessionId: sessionId,
              sampleRate: SAMPLE_RATE,
              channels: CHANNELS,
              service: 'azure_speech',  // Specify Azure Speech
              language_pair: languagePair,  // Include language settings
              language_set: 'indian'  // Use Indian language set for Central India
            }))
            console.log('Azure Speech init_session message sent successfully')
          } catch (error) {
            console.error('Error sending Azure init message:', error)
            reject(error)
            return
          }
          
          resolve(ws)
        }
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            handleAzureWebSocketMessage(data)  // Updated handler
          } catch (e) {
            console.error('Error parsing WebSocket message:', e)
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          onConnectionChange('error')
          setIsWebSocketConnected(false)
          setError('WebSocket connection failed')
          reject(new Error('WebSocket connection failed'))
        }
        
        ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          
          // Only handle if this is the current WebSocket
          if (websocketRef.current === ws) {
            onConnectionChange('disconnected')
            setIsWebSocketConnected(false)
            setIsCapturing(false)
          }
        }
        
        // Set a timeout for connection
        setTimeout(() => {
          if (ws.readyState !== WebSocket.OPEN) {
            ws.close()
            reject(new Error('WebSocket connection timeout'))
          }
        }, 10000) // 10 second timeout
      
      } catch (error) {
        console.error('Failed to create Azure Speech WebSocket:', error)
        onConnectionChange('error')
        setIsWebSocketConnected(false)
        setError('Failed to create Azure Speech WebSocket connection')
        reject(error)
      }
    })
  }, [onConnectionChange, onSessionStart, languagePair])

  const disconnectWebSocket = useCallback(() => {
    try {
      if (websocketRef.current) {
        console.log('Disconnecting WebSocket...')
        websocketRef.current.close(1000, 'User disconnected')
        websocketRef.current = null
      }
      sessionIdRef.current = ''
      setIsWebSocketConnected(false)
      onConnectionChange('disconnected')
      console.log('WebSocket disconnected')
    } catch (error) {
      console.error('Error disconnecting WebSocket:', error)
    }
  }, [onConnectionChange])

  // Update message handler for Azure Speech
  const handleAzureWebSocketMessage = useCallback((data: any) => {
    try {
      switch (data.type) {
        case 'partial_transcript':
          // Now includes both original and translated text
          onTranscriptUpdate({
            id: `partial_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: 'partial',
            original: data.original || data.text,  // Support both new and old format
            translated: data.translated || data.text,  // Use translated if available
            timestamp: data.timestamp,
            hasTranslation: data.has_translation || false
          })
          break
          
        case 'final_transcript':
          onTranscriptUpdate({
            id: `final_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: 'final',
            original: data.original,
            translated: data.translated || data.original,  // Use translated text if available
            detectedLanguage: data.detectedLanguage || 'unknown',
            confidence: data.confidence || 0.9,
            timestamp: data.timestamp
          })
          break
          
        case 'session_confirmed':
          console.log('Azure Speech session confirmed:', data)
          if (data.multilingual_support) {
            console.log('✅ Multilingual support enabled')
          }
          if (data.auto_language_detection) {
            console.log('✅ Automatic language detection enabled')
          }
          break
          
        case 'connection_status':
          console.log('Azure Speech connection status:', data)
          if (data.azure_speech_connected) {
            console.log('✅ Azure Speech Services connected')
            if (data.multilingual_enabled) {
              console.log('✅ Multilingual processing active')
            }
          } else {
            console.warn('Azure Speech connection failed:', data.message)
          }
          break
          
        case 'ack':
          // Audio frame acknowledgment
          if (data.seq % 100 === 0) {
            console.log(`Azure Speech processed ${data.seq} audio frames`)
          }
          break
          
        case 'error':
          console.error('Azure Speech error:', data.message)
          setError(`Azure Speech: ${data.message}`)
          onConnectionChange('error')
          break
          
        default:
          console.log('Unknown Azure Speech message type:', data.type, data)
      }
    } catch (error) {
      console.error('Error handling Azure Speech WebSocket message:', error)
    }
  }, [onTranscriptUpdate, onConnectionChange])

  const startAudioCapture = useCallback(async () => {
    // Prevent multiple simultaneous calls
    if (isCapturing) {
      console.log('Audio capture already in progress')
      return
    }
    
    try {
      setError('')
      
      // Clean up individual components without closing WebSocket
      if (mediaStreamRef.current) {
        console.log('Cleaning up previous media stream...')
        mediaStreamRef.current.getTracks().forEach(track => track.stop())
        mediaStreamRef.current = null
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        console.log('Cleaning up previous audio context...')
        try {
          audioContextRef.current.close()
        } catch (error) {
          console.error('Error closing audio context:', error)
        }
        audioContextRef.current = null
      }
      // Don't call stopAudioCapture() here - it would close the WebSocket!
      
      console.log('Starting WebSocket connection...')
      // Connect WebSocket first and wait for connection
      await connectWebSocket()
      
      // Wait a bit for WebSocket to be fully established
      await new Promise(resolve => setTimeout(resolve, 200))
      
      console.log('WebSocket connection established, proceeding with audio setup...')
      
      // Show user instruction for tab selection
      console.log('Please select a tab that has audio (like a meeting tab)')
      
      // Request tab capture (must include video, but we'll only use audio)
      const stream = await navigator.mediaDevices.getDisplayMedia({
        audio: {
          sampleRate: SAMPLE_RATE,
          channelCount: CHANNELS,
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        },
        video: true // Required by getDisplayMedia API
      })
      
      // Extract only the audio track from the stream
      const audioTrack = stream.getAudioTracks()[0]
      if (!audioTrack) {
        // Stop all tracks and throw error
        stream.getTracks().forEach(track => track.stop())
        throw new Error('No audio track found in the selected tab. Please select a tab that has audio (like a meeting tab).')
      }
      
      console.log('Audio track found:', {
        id: audioTrack.id,
        label: audioTrack.label,
        enabled: audioTrack.enabled,
        muted: audioTrack.muted,
        readyState: audioTrack.readyState
      })
      
      // Create a new MediaStream with only the audio track
      const audioOnlyStream = new MediaStream([audioTrack])
      
      // Stop all video tracks to free up resources
      stream.getVideoTracks().forEach(track => {
        track.stop()
      })
      
      mediaStreamRef.current = audioOnlyStream
      
              console.log('Audio stream created with', audioOnlyStream.getTracks().length, 'tracks')
        
                // Create audio context with forced 16kHz sample rate for AssemblyAI
        const audioContext = new AudioContext({
          sampleRate: 16000,  // Force 16kHz for AssemblyAI compatibility
          latencyHint: 'interactive'
        })
      audioContextRef.current = audioContext
      
      console.log('Audio context created:', {
        sampleRate: audioContext.sampleRate,
        state: audioContext.state,
        baseLatency: audioContext.baseLatency,
        outputLatency: audioContext.outputLatency
      })
      
              // Resume audio context if it's suspended
        if (audioContext.state === 'suspended') {
          console.log('Resuming suspended audio context...')
          await audioContext.resume()
          console.log('Audio context resumed, new state:', audioContext.state)
        }
        
        // Ensure audio context is running
        if (audioContext.state !== 'running') {
          console.log('Audio context not running, current state:', audioContext.state)
          // Try to resume again
          await audioContext.resume()
          console.log('Audio context state after resume:', audioContext.state)
        }
      
              // Create audio source from audio-only stream
        const source = audioContext.createMediaStreamSource(audioOnlyStream)
        
        // Simple audio level test to verify audio is being captured
        const testAnalyser = audioContext.createAnalyser()
        testAnalyser.fftSize = 256
        source.connect(testAnalyser)
        
        // Check for audio data after a short delay
        setTimeout(() => {
          try {
            const testDataArray = new Uint8Array(testAnalyser.frequencyBinCount)
            testAnalyser.getByteFrequencyData(testDataArray)
            const testAverage = testDataArray.reduce((a, b) => a + b) / testDataArray.length
            console.log('Audio level test:', testAverage)
            setAudioLevel(testAverage / 255)
          } catch (error) {
            console.error('Error testing audio level:', error)
          } finally {
            // Always disconnect test analyser
            try {
              source.disconnect(testAnalyser)
            } catch (error) {
              console.error('Error disconnecting test analyser:', error)
            }
          }
        }, 1000)
        
        // Create ScriptProcessor for audio processing (like reference file)
        const processor = audioContext.createScriptProcessor(FRAME_SIZE, CHANNELS, CHANNELS)
        processorRef.current = processor
        
        // Set up audio processing with frame buffering
        processor.onaudioprocess = (event) => {
          if (websocketRef.current?.readyState === WebSocket.OPEN) {
            try {
              const inputBuffer = event.inputBuffer
              const inputData = inputBuffer.getChannelData(0)
              
              // Add to frame buffer (like reference file)
              frameBufferRef.current.push(new Float32Array(inputData))
              
              // Process frames when we have enough samples
              processAudioFrames()
            } catch (error) {
              console.error('Error processing audio frame:', error)
            }
          }
        }
        
        // Connect the audio nodes
        source.connect(processor)
        processor.connect(audioContext.destination)
        
        console.log('ScriptProcessor created and connected successfully with frame buffering')
      

      
      setIsCapturing(true)
      console.log('Audio capture started successfully')
      
    } catch (error) {
      console.error('Failed to start audio capture:', error)
      
      // Clean up any partial setup
      if (websocketRef.current) {
        websocketRef.current.close(1000, 'Setup failed')
        websocketRef.current = null
      }
      
      setError(error instanceof Error ? error.message : 'Failed to start audio capture')
      onConnectionChange('error')
      
      // Reset state
      setIsCapturing(false)
    }
  }, [connectWebSocket, generateSessionId, onSessionStart, onConnectionChange, isCapturing])

  // Start recording audio to file (for testing)
  const startAudioRecording = useCallback(async () => {
    if (!mediaStreamRef.current) {
      setError('No audio stream available. Please start audio capture first.')
      return
    }
    
    try {
      setIsRecording(true)
      recordedChunksRef.current = []
      
      // Create MediaRecorder with WAV format
      const mediaRecorder = new MediaRecorder(mediaStreamRef.current, {
        mimeType: 'audio/webm;codecs=opus' // Most compatible format
      })
      
      mediaRecorderRef.current = mediaRecorder
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(recordedChunksRef.current, { type: 'audio/webm' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setRecordedAudioUrl(audioUrl)
        setIsRecording(false)
        console.log('Audio recording completed, file size:', audioBlob.size, 'bytes')
      }
      
      // Start recording
      mediaRecorder.start(1000) // Collect data every second
      console.log('Audio recording started')
      
    } catch (error) {
      console.error('Failed to start audio recording:', error)
      setError('Failed to start audio recording')
      setIsRecording(false)
    }
  }, [])
  
  // Stop recording audio
  const stopAudioRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      console.log('Audio recording stopped')
    }
  }, [])
  
  // Download recorded audio
  const downloadRecordedAudio = useCallback(() => {
    if (recordedAudioUrl) {
      const a = document.createElement('a')
      a.href = recordedAudioUrl
      a.download = `audio_test_${Date.now()}.webm`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      console.log('Audio file download started')
    }
  }, [recordedAudioUrl])
  
  // Process audio frames and send to backend (like reference file)
  const processAudioFrames = useCallback(() => {
    if (!websocketRef.current || frameBufferRef.current.length === 0) {
      return
    }

    try {
      // Calculate how many samples we have
      const totalSamples = frameBufferRef.current.reduce((sum, frame) => sum + frame.length, 0)
      
      // If we have enough samples for a complete frame, process them
      if (totalSamples >= FRAME_SIZE) {
        // Accumulate samples from buffer
        let accumulatedSamples: number[] = []
        
        // Collect all available samples
        while (frameBufferRef.current.length > 0) {
          const frame = frameBufferRef.current.shift()
          if (!frame) continue
          accumulatedSamples.push(...Array.from(frame))
        }
        
        // Process complete frames
        while (accumulatedSamples.length >= FRAME_SIZE) {
          // Extract exactly the samples we need for this frame
          const frameSamples = accumulatedSamples.splice(0, FRAME_SIZE)
          
                     // Convert Float32 to Int16 PCM
           const pcmData = new Int16Array(FRAME_SIZE)
           let hasAudio = false
           let minSample = 0
           let maxSample = 0
           
           for (let i = 0; i < FRAME_SIZE; i++) {
             const sample = Math.max(-1, Math.min(1, frameSamples[i]))
             pcmData[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF
             
             // Track audio levels for validation
             if (Math.abs(sample) > 0.01) {  // Threshold for "silence"
               hasAudio = true
             }
             minSample = Math.min(minSample, pcmData[i])
             maxSample = Math.max(maxSample, pcmData[i])
           }
           
           // Log audio validation every 10th frame
           if (Math.random() < 0.1) {  // 10% chance to log
             console.log(`🎵 Audio validation - Has audio: ${hasAudio}, Range: ${minSample} to ${maxSample}`)
           }
           
           // Skip sending if completely silent
           if (!hasAudio) {
             console.log('🔇 Skipping silent audio frame')
             continue
           }
          
          // Send to backend
          if (websocketRef.current?.readyState === WebSocket.OPEN) {
            websocketRef.current.send(pcmData.buffer)
            console.log('Sent audio frame:', pcmData.buffer.byteLength, 'bytes')
          }
        }
        
        // Put remaining samples back if any
        if (accumulatedSamples.length > 0) {
          frameBufferRef.current.push(new Float32Array(accumulatedSamples))
        }
      }
    } catch (error) {
      console.error('Error processing audio frames:', error)
    }
  }, [])

  const stopAudioCapture = useCallback(() => {
    console.trace('stopAudioCapture called from:')
    console.log('Current state:', {
      isCapturing,
      isWebSocketConnected,
      connectionState
    })
    try {
      // Stop media stream
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop())
        mediaStreamRef.current = null
      }
      
      // Disconnect processor first (before setting to null)
      if (processorRef.current) {
        try {
          if (typeof processorRef.current.disconnect === 'function') {
            processorRef.current.disconnect()
          }
        } catch (error) {
          console.error('Error disconnecting processor:', error)
        }
        processorRef.current = null
      }
      
      // Clear intervals
      if (audioLevelIntervalRef.current) {
        clearInterval(audioLevelIntervalRef.current)
        audioLevelIntervalRef.current = null
      }
      if (testAudioIntervalRef.current) {
        clearInterval(testAudioIntervalRef.current)
        testAudioIntervalRef.current = null
      }
      
      // Cancel animation frame
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
      
      // Close audio context
      if (audioContextRef.current) {
        try {
          if (audioContextRef.current.state !== 'closed') {
            audioContextRef.current.close()
          }
        } catch (error) {
          console.error('Error closing audio context:', error)
        }
        audioContextRef.current = null
      }
      
             // Clear frame buffer
       frameBufferRef.current = []
       
       // Clean up MediaRecorder
       if (mediaRecorderRef.current) {
         try {
           if (mediaRecorderRef.current.state === 'recording') {
             mediaRecorderRef.current.stop()
           }
         } catch (error) {
           console.error('Error stopping MediaRecorder:', error)
         }
         mediaRecorderRef.current = null
       }
       
       // Clear recorded audio
       if (recordedAudioUrl) {
         URL.revokeObjectURL(recordedAudioUrl)
         setRecordedAudioUrl('')
       }
       recordedChunksRef.current = []
       setIsRecording(false)
       
       setIsCapturing(false)
       console.log('Audio capture stopped')
      
    } catch (error) {
      console.error('Error stopping audio capture:', error)
    }
  }, [onConnectionChange])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAudioCapture()
    }
  }, [])

  // Update WebSocket when language pair changes
  useEffect(() => {
    if (websocketRef.current?.readyState === WebSocket.OPEN && sessionIdRef.current) {
      websocketRef.current.send(JSON.stringify({
        type: 'update_language',
        language_pair: languagePair
      }))
    }
  }, [languagePair])
  
  // Keep connection alive with periodic pings
  useEffect(() => {
    if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
      return
    }
    
    const pingInterval = setInterval(() => {
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        try {
          websocketRef.current.send(JSON.stringify({ type: 'ping' }))
        } catch (error) {
          console.error('Error sending ping:', error)
        }
      }
    }, 30000) // Send ping every 30 seconds
    
    return () => clearInterval(pingInterval)
  }, [])
   
   // Keep audio capture alive with periodic checks
   useEffect(() => {
     if (!isCapturing || !websocketRef.current) {
       return
     }
     
     const keepAliveInterval = setInterval(() => {
       if (isCapturing && websocketRef.current?.readyState === WebSocket.OPEN) {
         console.log('🔋 Audio capture keep-alive check - all systems operational')
         
         // Check if audio context is still running
         if (audioContextRef.current && audioContextRef.current.state !== 'running') {
           console.warn('⚠️ Audio context not running, attempting to resume...')
           try {
             audioContextRef.current.resume()
           } catch (error) {
             console.error('Error resuming audio context:', error)
           }
         }
         
         // Check if processor is still connected
         if (processorRef.current && !processorRef.current.context) {
           console.warn('⚠️ Audio processor disconnected, audio capture may have stopped')
         }
       }
     }, 10000) // Check every 10 seconds
     
     return () => clearInterval(keepAliveInterval)
   }, [isCapturing])

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {/* WebSocket Connection Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            isWebSocketConnected ? 'bg-green-500' : 'bg-gray-400'
          }`} />
          <span className="text-sm font-medium">
            WebSocket: {isWebSocketConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        {/* Audio Capture Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            isCapturing ? 'bg-blue-500' : 'bg-gray-400'
          }`} />
          <span className="text-sm font-medium">
            Audio: {isCapturing ? 'Capturing' : 'Stopped'}
          </span>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* WebSocket Connection Management */}
      <div className="space-y-3 border-b border-gray-200 pb-4">
        <div className="text-sm font-medium text-gray-700">WebSocket Connection:</div>
        {!isWebSocketConnected ? (
          <button
            onClick={connectWebSocket}
            disabled={connectionState === 'connecting'}
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            <Monitor className="w-5 h-5" />
            <span>Connect WebSocket</span>
          </button>
        ) : (
          <button
            onClick={disconnectWebSocket}
            className="btn-danger w-full flex items-center justify-center space-x-2"
          >
            <Square className="w-5 h-5" />
            <span>Disconnect WebSocket</span>
          </button>
        )}
      </div>

      {/* Audio Capture Management */}
      <div className="space-y-3">
          {!isCapturing ? (
            <button
              onClick={startAudioCapture}
              disabled={!isWebSocketConnected || connectionState === 'connecting'}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              <Monitor className="w-5 h-5" />
              <span>Start Capturing Meeting Audio</span>
            </button>
          ) : (
            <button
              onClick={stopAudioCapture}
              className="btn-danger w-full flex items-center justify-center space-x-2"
            >
              <Square className="w-5 h-5" />
              <span>Stop Audio Capture</span>
            </button>
          )}
          
          {/* Audio Recording for Testing */}
          {isCapturing && (
            <div className="space-y-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <div className="text-sm font-medium text-blue-700">🎵 Audio Recording Test:</div>
              {!isRecording ? (
                <button
                  onClick={startAudioRecording}
                  className="btn-secondary w-full flex items-center justify-center space-x-2"
                >
                  <Mic className="w-5 h-5" />
                  <span>Start Recording Audio File</span>
                </button>
              ) : (
                <button
                  onClick={stopAudioRecording}
                  className="btn-danger w-full flex items-center justify-center space-x-2"
                >
                  <Square className="w-5 h-5" />
                  <span>Stop Recording</span>
                </button>
              )}
              
              {recordedAudioUrl && (
                <button
                  onClick={downloadRecordedAudio}
                  className="btn-primary w-full flex items-center justify-center space-x-2"
                >
                  <MicOff className="w-5 h-5" />
                  <span>Download Recorded Audio</span>
                </button>
              )}
            </div>
          )}
         
                           {/* Test Audio Button */}
        {isCapturing && isWebSocketConnected && (
          <div className="space-y-2">
            <button
              onClick={() => {
                if (websocketRef.current?.readyState === WebSocket.OPEN) {
                  // Send a test audio frame
                  const testFrame = new Int16Array(FRAME_SIZE).fill(0)
                  console.log('Sending test audio frame:', testFrame.buffer.byteLength, 'bytes')
                  websocketRef.current.send(testFrame.buffer)
                }
              }}
              className="btn-secondary w-full flex items-center justify-center space-x-2"
            >
              <Mic className="w-5 h-5" />
              <span>Send Test Audio Frame</span>
            </button>
              
              <button
                onClick={() => {
                  // Test audio context state
                  if (audioContextRef.current) {
                    console.log('Audio context state:', audioContextRef.current.state)
                    console.log('Audio context sample rate:', audioContextRef.current.sampleRate)
                  }
                  
                  // Test media stream
                  if (mediaStreamRef.current) {
                    const tracks = mediaStreamRef.current.getTracks()
                    console.log('Media stream tracks:', tracks.map(t => ({
                      id: t.id,
                      kind: t.kind,
                      enabled: t.enabled,
                      muted: t.muted,
                      readyState: t.readyState
                    })))
                  }
                }}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <MicOff className="w-5 h-5" />
                <span>Debug Audio State</span>
              </button>
            </div>
          )}
       </div>

             {/* Audio Level Meter */}
       {isCapturing && (
         <div className="space-y-2">
           <div className="text-xs text-gray-600">Audio Level:</div>
           <div className="w-full bg-gray-200 rounded-full h-2">
             <div 
               className="bg-blue-600 h-2 rounded-full transition-all duration-100"
               style={{ width: `${Math.min(100, audioLevel * 100)}%` }}
             />
           </div>
           <div className="text-xs text-gray-500">
             {audioLevel > 0 ? `Level: ${(audioLevel * 100).toFixed(1)}%` : 'No audio detected'}
           </div>
         </div>
       )}
       
               <div className="text-xs text-gray-600 space-y-1">
          <p>• Audio will be captured from your meeting tab</p>
          <p>• Sample rate: 16kHz, Mono channel (Azure Speech requirement)</p>
          <p>• Frame size: 128ms (2048 samples) - power of 2</p>
          <p>• Real-time streaming to Azure Speech Services</p>
          <p>• 🌍 Multilingual support with automatic language detection</p>
        </div>
    </div>
  )
}

export default AudioCapture
