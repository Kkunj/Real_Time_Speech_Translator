#!/usr/bin/env python3
"""
Speech Translator Backend - Stage 1
FastAPI WebSocket server for receiving audio frames from browser
"""

import asyncio
import json
import logging
import os
import time
import wave
from datetime import datetime
from typing import Dict, Any

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from assemblyai_asr_service import AssemblyAIASRService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Speech Translator Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AudioSession:
    """Manages audio session state and frame processing with ASR"""
    
    def __init__(self, session_id: str, sample_rate: int = 48000, channels: int = 1):
        self.session_id = session_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_duration_ms = 100
        self.samples_per_frame = int((sample_rate * self.frame_duration_ms) / 1000)
        self.bytes_per_frame = self.samples_per_frame * 2  # 16-bit samples
        
        # Audio buffer for reconstruction
        self.audio_buffer = bytearray()
        self.frame_count = 0
        self.last_frame_time = None
        
        # AssemblyAI streaming session
        self.asr_streaming_started = False
        
        # ASR service
        try:
            self.asr_service = AssemblyAIASRService()
            logger.info(f"AssemblyAI ASR service initialized for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize AssemblyAI ASR service: {e}")
            self.asr_service = None
        
        # Create output directory
        self.output_dir = f"audio_output/{session_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Created session {session_id}: {sample_rate}Hz, {channels}ch, "
                   f"{self.samples_per_frame} samples/frame, {self.bytes_per_frame} bytes/frame, "
                   f"AssemblyAI streaming enabled")
    
    async def add_frame(self, frame_data: bytes, timestamp: float, websocket: WebSocket = None) -> Dict[str, Any]:
        """Add audio frame and return processing info"""
        self.frame_count += 1
        self.last_frame_time = timestamp
        
        # Validate frame size
        expected_size = self.bytes_per_frame
        actual_size = len(frame_data)
        
        if actual_size != expected_size:
            logger.warning(f"Frame {self.frame_count}: expected {expected_size} bytes, got {actual_size}")
        
        # Add to buffer
        self.audio_buffer.extend(frame_data)
        
        # Stream audio directly to AssemblyAI for real-time processing
        if self.asr_service and websocket:
            # Start AssemblyAI streaming if not already started
            if not self.asr_service.is_connected:
                try:
                    await self.asr_service.start_streaming(self.sample_rate)
                    logger.info("AssemblyAI streaming started for real-time ASR")
                except Exception as e:
                    logger.error(f"Failed to start AssemblyAI streaming: {e}")
                    return
            
            # Process audio frame directly through AssemblyAI
            await self._process_audio_frame_realtime(frame_data, websocket)
        
        # Calculate RTT if we have timing info
        rtt_ms = None
        if hasattr(self, 'send_time'):
            rtt_ms = (timestamp - self.send_time) * 1000
        
        return {
            "frame_number": self.frame_count,
            "frame_size_bytes": actual_size,
            "expected_size_bytes": expected_size,
            "buffer_size_bytes": len(self.audio_buffer),
            "rtt_ms": rtt_ms
        }
    
    async def _process_audio_frame_realtime(self, frame_data: bytes, websocket: WebSocket):
        """Process audio frame in real-time through AssemblyAI"""
        try:
            logger.debug(f"Processing real-time audio frame: {len(frame_data)} bytes")
            
            # Set up callbacks for AssemblyAI results
            async def on_partial(text: str, timestamp: float):
                await self._send_asr_partial(websocket, text, len(frame_data))
            
            async def on_final(text: str, timestamp: float):
                await self._send_asr_final(websocket, text, len(frame_data))
            
            # Configure AssemblyAI callbacks (only once)
            if not hasattr(self.asr_service, '_callbacks_configured'):
                self.asr_service.set_callbacks(
                    on_partial=lambda text, ts: asyncio.create_task(on_partial(text, ts)),
                    on_final=lambda text, ts: asyncio.create_task(on_final(text, ts))
                )
                self.asr_service._callbacks_configured = True
                logger.info("AssemblyAI callbacks configured for this session")
            
            # Process audio frame through AssemblyAI (this should trigger callbacks)
            await self.asr_service.process_audio_chunk(frame_data, self.sample_rate)
            
        except Exception as e:
            logger.error(f"Error processing real-time audio frame: {e}")
            import traceback
            traceback.print_exc()
    
    async def _send_asr_partial(self, websocket: WebSocket, text: str, frame_size: int):
        """Send partial ASR result to client"""
        try:
            message = {
                "type": "asr_partial",
                "text": text,
                "seq": self.frame_count,
                "timestamp": time.time()
            }
            await websocket.send_text(json.dumps(message))
            logger.info(f"✅ Sent partial ASR to frontend: '{text}'")
        except Exception as e:
            logger.error(f"❌ Failed to send partial ASR: {e}")
            import traceback
            traceback.print_exc()
    
    async def _send_asr_final(self, websocket: WebSocket, text: str, frame_size: int):
        """Send final ASR result to client"""
        try:
            message = {
                "type": "asr_final",
                "text": text,
                "seq": self.frame_count,
                "timestamp": time.time()
            }
            await websocket.send_text(json.dumps(message))
            logger.info(f"Sent final ASR: {text}")
        except Exception as e:
            logger.error(f"Failed to send final ASR: {e}")
    
    def save_audio(self, filename: str = None) -> str:
        """Save accumulated audio buffer to WAV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"received_{timestamp}.wav"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert bytes to 16-bit PCM samples
        audio_data = np.frombuffer(self.audio_buffer, dtype=np.int16)
        
        # Save as WAV file
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        logger.info(f"Saved audio to {filepath}: {len(audio_data)} samples, "
                   f"{len(self.audio_buffer)} bytes, {self.frame_count} frames")
        
        return filepath
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        duration_seconds = len(self.audio_buffer) / (self.sample_rate * self.channels * 2)
        
        return {
            "session_id": self.session_id,
            "frame_count": self.frame_count,
            "total_bytes": len(self.audio_buffer),
            "duration_seconds": duration_seconds,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "samples_per_frame": self.samples_per_frame,
            "bytes_per_frame": self.bytes_per_frame
        }

# Active sessions
active_sessions: Dict[str, AudioSession] = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Speech Translator Backend",
        "version": "1.0.0",
        "stage": "Stage 1 - Audio Capture POC",
        "endpoints": {
            "websocket": "/ws",
            "sessions": "/sessions",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/sessions")
async def list_sessions():
    """List active audio sessions"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": session_id,
                "stats": session.get_stats()
            }
            for session_id, session in active_sessions.items()
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for audio streaming"""
    await websocket.accept()
    session_id = None
    session: AudioSession = None
    
    try:
        logger.info(f"WebSocket connection established")
        
        # Wait for session initialization
        init_message = await websocket.receive_text()
        init_data = json.loads(init_message)
        
        if init_data.get("type") != "session_init":
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Expected session_init message"
            }))
            return
        
        # Extract session parameters
        session_id = init_data["sessionId"]
        sample_rate = init_data.get("sampleRate", 48000)
        channels = init_data.get("channels", 1)
        frame_duration_ms = init_data.get("frameDurationMs", 100)
        
        # Create or get session
        if session_id in active_sessions:
            session = active_sessions[session_id]
            logger.info(f"Reusing existing session: {session_id}")
        else:
            session = AudioSession(session_id, sample_rate, channels)
            active_sessions[session_id] = session
            logger.info(f"Created new session: {session_id}")
        
        # Send session confirmation
        await websocket.send_text(json.dumps({
            "type": "session_confirmed",
            "sessionId": session_id,
            "sampleRate": sample_rate,
            "channels": channels,
            "frameDurationMs": frame_duration_ms
        }))
        
        logger.info(f"Session {session_id} initialized, waiting for audio frames...")
        
        # Process incoming audio frames
        frame_count = 0
        while True:
            try:
                # Receive binary audio frame
                frame_data = await websocket.receive_bytes()
                frame_count += 1
                receive_time = time.time()
                
                # Process frame
                frame_info = await session.add_frame(frame_data, receive_time, websocket)
                
                # Send acknowledgment
                ack_message = {
                    "type": "ack",
                    "seq": frame_count,
                    "timestamp": receive_time,
                    "frame_info": frame_info
                }
                
                await websocket.send_text(json.dumps(ack_message))
                
                # Log every 100th frame to avoid spam
                if frame_count % 100 == 0:
                    logger.info(f"Session {session_id}: received {frame_count} frames, "
                               f"buffer size: {len(session.audio_buffer)} bytes")
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error processing frame in session {session_id}: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Frame processing error: {str(e)}"
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket.client_state.value < 3:  # Still connected
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }))
    
    finally:
        # Cleanup session
        if session_id and session_id in active_sessions:
            if session:
                # Stop AssemblyAI streaming
                if session.asr_service and session.asr_service.is_connected:
                    logger.info("Stopping AssemblyAI streaming session")
                    try:
                        await session.asr_service.stop_streaming()
                        logger.info("AssemblyAI streaming stopped")
                    except Exception as e:
                        logger.error(f"Failed to stop AssemblyAI streaming: {e}")
                
                # Save final audio
                try:
                    output_file = session.save_audio("final_audio.wav")
                    logger.info(f"Session {session_id} ended, saved final audio to {output_file}")
                except Exception as e:
                    logger.error(f"Failed to save final audio for session {session_id}: {e}")
            
            # Keep session data for inspection (don't delete immediately)
            logger.info(f"Session {session_id} cleanup complete")

if __name__ == "__main__":
    import uvicorn
    
    # Create audio output directory
    os.makedirs("audio_output", exist_ok=True)
    
    logger.info("Starting Speech Translator Backend...")
    logger.info("Stage 1: Audio Capture POC")
    logger.info("WebSocket endpoint: ws://localhost:8000/ws")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
