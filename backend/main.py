from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio
import logging
import time
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading

# Azure Speech Services imports
import azure.cognitiveservices.speech as speechsdk
import azure.cognitiveservices.speech.translation as speech_translation
from azure.cognitiveservices.speech.translation import SpeechTranslationConfig, TranslationRecognizer
from azure.cognitiveservices.speech import AudioConfig, AutoDetectSourceLanguageConfig

# Azure Translator Service import - REMOVED for Phase 1 optimization
# from azure_translator import translator_service

# Mock translator service to prevent any accidental calls
class MockTranslatorService:
    def is_available(self):
        return False
    
    def translate_text(self, *args, **kwargs):
        logger.warning("Azure Translator API calls are disabled for Phase 1 optimization")
        return None
    
    def get_service_info(self):
        return {"available": False, "message": "Disabled for Phase 1 optimization"}
    
    def get_supported_languages(self):
        return {"languages": [], "message": "Disabled for Phase 1 optimization"}

# Create mock instance to prevent any accidental imports
translator_service = MockTranslatorService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Real-Time Speech Translator", version="1.0.0")

# Add CORS middleware for Render deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "https://live-speech-frontend.onrender.com",  # Your Render frontend domain
        "https://live-speech-v2.onrender.com",  # Alternative frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Speech Configuration - Use environment variables for security
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "your-azure-speech-key")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "centralindia")  # Central India region

class AzureSpeechSession:
    """Manages Azure Speech Service session with multilingual support"""
    
    def __init__(self, session_id: str, sample_rate: int = 16000, channels: int = 1):
        self.session_id = session_id
        self.sample_rate = sample_rate
        self.channels = channels
        
        # Azure Speech configuration
        self.speech_config = None
        self.translation_config = None
        self.recognizer = None
        self.translator = None
        
        # Audio stream
        self.audio_stream = None
        self.push_stream = None
        
        # Session state
        self.is_active = False
        self.websocket = None
        self.websocket_closed = False
        
        # Language settings
        self.source_language = "auto"  # Auto-detect by default
        self.target_language = "en"
        # Azure auto-detection only supports 4 languages at a time
        # Using the most common languages for optimal performance
        self.supported_languages = [
            "en-US", "hi-IN", "es-ES", "fr-FR"  # English, Hindi, Spanish, French
        ]
        
        # Alternative language sets for different scenarios
        self.language_sets = {
            "business": ["en-US", "es-ES", "fr-FR", "de-DE"],
            "tech": ["en-US", "zh-CN", "ja-JP", "hi-IN"],
            "european": ["en-GB", "de-DE", "fr-FR", "it-IT"],
            "indian": ["en-IN", "hi-IN", "bn-IN", "te-IN"]
        }
        
        logger.info(f"Created Azure Speech session {session_id}: {sample_rate}Hz, {channels}ch")
    
    async def initialize_speech_services(self):
        """Initialize Azure Speech Services with multilingual support"""
        try:
            # Speech-to-Text configuration with auto language detection
            self.speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY,
                region=AZURE_SPEECH_REGION
            )
            
            # Note: These properties are not available in Azure Speech SDK 1.45.0
            # Continuous recognition is enabled by default
            # Audio format is handled automatically by the SDK
            
            # Translation configuration for multilingual support
            self.translation_config = speech_translation.SpeechTranslationConfig(
                subscription=AZURE_SPEECH_KEY,
                region=AZURE_SPEECH_REGION
            )
            
            # Set target language for translation
            self.translation_config.add_target_language(self.target_language)
            
            # Configure auto language detection
            if self.source_language == "auto":
                # Create auto-detect configuration
                auto_detect_config = AutoDetectSourceLanguageConfig(
                    languages=self.supported_languages
                )
                self.auto_detect_config = auto_detect_config
            else:
                self.translation_config.speech_recognition_language = self.source_language
            
            # Create push audio stream with proper format
            audio_format = speechsdk.audio.AudioStreamFormat(
                samples_per_second=16000,  # 16kHz sample rate
                bits_per_sample=16,        # 16-bit audio
                channels=1                 # Mono audio
            )
            self.push_stream = speechsdk.audio.PushAudioInputStream(audio_format)
            self.audio_config = speechsdk.audio.AudioConfig(stream=self.push_stream)
            
            logger.info(f"Azure Speech Services initialized for session: {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech Services: {e}")
            return False
    
    async def start_recognition(self, websocket):
        """Start continuous speech recognition with translation"""
        try:
            self.websocket = websocket
            
            # Initialize services
            if not await self.initialize_speech_services():
                return False
            
            # Create recognizer based on language detection mode
            if self.source_language == "auto":
                # Use translation recognizer with auto-detection
                self.translator = speech_translation.TranslationRecognizer(
                    translation_config=self.translation_config,
                    audio_config=self.audio_config,
                    auto_detect_source_language_config=self.auto_detect_config
                )
                
                # Set up event handlers for translation
                self.translator.recognizing.connect(self._on_recognizing_translation)
                self.translator.recognized.connect(self._on_recognized_translation)
                self.translator.canceled.connect(self._on_canceled)
                self.translator.session_started.connect(self._on_session_started)
                self.translator.session_stopped.connect(self._on_session_stopped)
                
                # Start continuous recognition
                await self._start_continuous_translation()
                
            else:
                # Use regular recognizer with specific language
                self.recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    audio_config=self.audio_config
                )
                
                # Set up event handlers
                self.recognizer.recognizing.connect(self._on_recognizing)
                self.recognizer.recognized.connect(self._on_recognized)
                self.recognizer.canceled.connect(self._on_canceled)
                self.recognizer.session_started.connect(self._on_session_started)
                self.recognizer.session_stopped.connect(self._on_session_stopped)
                
                # Start continuous recognition
                await self._start_continuous_recognition()
            
            self.is_active = True
            logger.info(f"Azure Speech recognition started for session: {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Azure Speech recognition: {e}")
            return False
    
    async def _start_continuous_recognition(self):
        """Start continuous recognition in thread pool"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, self.recognizer.start_continuous_recognition)
    
    async def _start_continuous_translation(self):
        """Start continuous translation in thread pool"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, self.translator.start_continuous_recognition)
    
    def _on_recognizing(self, evt):
        """Handle partial recognition results"""
        try:
            if self.websocket and evt.result.text.strip():
                # Use threading to avoid async issues
                import threading
                def send_partial():
                    try:
                        import asyncio
                        # Create new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(self._send_partial_result(evt.result.text))
                        finally:
                            loop.close()
                    except Exception as e:
                        logger.error(f"Error sending partial result: {e}")
                
                threading.Thread(target=send_partial, daemon=True).start()
        except Exception as e:
            logger.error(f"Error in recognizing: {e}")
    
    def _on_recognized(self, evt):
        """Handle final recognition results - no translation for non-translation mode"""
        try:
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                detected_language = evt.result.language if hasattr(evt.result, 'language') else 'unknown'
                
                # In non-translation mode, just send the original text
                translated_text = evt.result.text  # No translation available
                logger.info(f"Regular recognition (no translation): '{evt.result.text[:30]}...'")
                
                if self.websocket:
                    # Use threading to avoid async issues
                    import threading
                    def send_final():
                        try:
                            import asyncio
                            # Create new event loop for this thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(self._send_final_result(
                                    original=evt.result.text,
                                    translated=translated_text,
                                    language=detected_language
                                ))
                            finally:
                                loop.close()
                        except Exception as e:
                            logger.error(f"Error sending final result: {e}")
                    
                    threading.Thread(target=send_final, daemon=True).start()
        except Exception as e:
            logger.error(f"Error in recognized: {e}")
    
    def _on_recognizing_translation(self, evt):
        """Handle partial translation results - show both original and translated"""
        try:
            if self.websocket and evt.result.text.strip():
                # Get partial translation if available
                partial_translated = ""
                if self.target_language in evt.result.translations:
                    partial_translated = evt.result.translations[self.target_language]
                
                # Use threading to avoid async issues
                import threading
                def send_partial():
                    try:
                        import asyncio
                        # Create new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(self._send_partial_result_with_translation(
                                original=evt.result.text,
                                translated=partial_translated
                            ))
                        finally:
                            loop.close()
                    except Exception as e:
                        logger.error(f"Error sending partial result: {e}")
                
                threading.Thread(target=send_partial, daemon=True).start()
        except Exception as e:
            logger.error(f"Error in recognizing translation: {e}")
    
    def _on_recognized_translation(self, evt):
        """Handle final translation results - USE ONLY Azure Speech translation"""
        try:
            if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
                # Get detected language
                detected_language = evt.result.language if hasattr(evt.result, 'language') else 'unknown'
                
                # USE ONLY Azure Speech built-in translation - NO API CALLS
                translated_text = ""
                if self.target_language in evt.result.translations:
                    translated_text = evt.result.translations[self.target_language]
                else:
                    # Fallback to original text if translation not available
                    translated_text = evt.result.text
                
                logger.info(f"Azure Speech direct translation: '{evt.result.text[:30]}...' -> '{translated_text[:30]}...'")
                
                if self.websocket:
                    # Use threading to avoid async issues
                    import threading
                    def send_final():
                        try:
                            import asyncio
                            # Create new event loop for this thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(self._send_final_result(
                                    original=evt.result.text,
                                    translated=translated_text,
                                    language=detected_language
                                ))
                            finally:
                                loop.close()
                        except Exception as e:
                            logger.error(f"Error sending final result: {e}")
                    
                    threading.Thread(target=send_final, daemon=True).start()
        except Exception as e:
            logger.error(f"Error in recognized translation: {e}")
    
    def _on_canceled(self, evt):
        """Handle recognition cancellation"""
        logger.error(f"Azure Speech recognition canceled: {evt.reason}")
        if evt.reason == speechsdk.CancellationReason.Error:
            logger.error(f"Error details: {evt.error_details}")
    
    def _on_session_started(self, evt):
        """Handle session start"""
        logger.info(f"Azure Speech session started: {evt.session_id}")
    
    def _on_session_stopped(self, evt):
        """Handle session stop"""
        logger.info(f"Azure Speech session stopped: {evt.session_id}")
        self.is_active = False
    
    async def _send_partial_result(self, text: str):
        """Send partial recognition result to client"""
        if self.websocket and text.strip():
            try:
                # Check if WebSocket is still connected
                if hasattr(self.websocket, 'client_state') and self.websocket.client_state.value == 3:  # WebSocketState.DISCONNECTED
                    logger.warning("WebSocket disconnected, skipping partial result")
                    return
                
                message = {
                    "type": "partial_transcript",
                    "text": text,
                    "timestamp": datetime.now().isoformat()
                }
                await self.websocket.send_text(json.dumps(message))
                logger.info(f"Sent partial result: {text[:50]}...")
            except Exception as e:
                logger.error(f"Failed to send partial result: {e}")

    async def _send_partial_result_with_translation(self, original: str, translated: str):
        """Send partial recognition result with translation to client"""
        if self.websocket and original.strip():
            try:
                # Check if WebSocket is still connected
                if hasattr(self.websocket, 'client_state') and self.websocket.client_state.value == 3:  # WebSocketState.DISCONNECTED
                    logger.warning("WebSocket disconnected, skipping partial result")
                    return
                
                message = {
                    "type": "partial_transcript",
                    "original": original,
                    "translated": translated if translated else original,  # Fallback to original
                    "timestamp": datetime.now().isoformat(),
                    "has_translation": bool(translated)
                }
                await self.websocket.send_text(json.dumps(message))
                logger.info(f"Sent partial with translation: {original[:30]}... -> {translated[:30] if translated else 'no translation'}...")
            except Exception as e:
                logger.error(f"Failed to send partial result with translation: {e}")
    
    async def _send_final_result(self, original: str, translated: str, language: str):
        """Send final recognition/translation result to client"""
        if self.websocket and original.strip():
            try:
                # Check if WebSocket is still connected
                if hasattr(self.websocket, 'client_state') and self.websocket.client_state.value == 3:  # WebSocketState.DISCONNECTED
                    logger.warning("WebSocket disconnected, skipping final result")
                    return
                
                message = {
                    "type": "final_transcript",
                    "original": original,
                    "translated": translated,
                    "detectedLanguage": language,
                    "confidence": 0.9,  # Azure doesn't provide detailed confidence
                    "timestamp": datetime.now().isoformat()
                }
                await self.websocket.send_text(json.dumps(message))
                logger.info(f"Sent final result: {original[:50]}... -> {translated[:50]}...")
            except Exception as e:
                logger.error(f"Failed to send final result: {e}")
    
    async def process_audio_frame(self, frame_data: bytes):
        """Process audio frame and send to Azure Speech"""
        if not self.is_active or not self.push_stream:
            return {"status": "inactive"}
        
        try:
            # Validate audio frame
            if len(frame_data) == 0:
                return {"status": "error", "error": "Empty audio frame"}
            
            # Check if frame size is reasonable (should be 2048 samples = 4096 bytes for 16kHz)
            expected_size = 4096  # 2048 samples * 2 bytes per sample
            if len(frame_data) != expected_size:
                logger.warning(f"Audio frame size mismatch: expected {expected_size}, got {len(frame_data)}")
            
            # Send audio data to Azure Speech stream
            self.push_stream.write(frame_data)
            
            return {
                "status": "processed",
                "frame_size": len(frame_data),
                "session_active": self.is_active,
                "expected_size": expected_size
            }
            
        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_audio_stats(self):
        """Get audio processing statistics"""
        return {
            "session_active": self.is_active,
            "supported_languages": self.supported_languages,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "sample_rate": self.sample_rate,
            "channels": self.channels
        }
    
    def update_language_settings(self, source_language: str = None, target_language: str = None, language_set: str = None):
        """Update language settings (requires restart of recognition)"""
        if source_language:
            self.source_language = source_language
        if target_language:
            self.target_language = target_language
        if language_set and language_set in self.language_sets:
            self.supported_languages = self.language_sets[language_set]
            logger.info(f"Language set updated to: {language_set}")
        
        logger.info(f"Language settings updated: {self.source_language} -> {self.target_language}")
        logger.info(f"Supported languages: {self.supported_languages}")
    
    def set_language_set(self, language_set: str):
        """Set a predefined language set for auto-detection"""
        if language_set in self.language_sets:
            self.supported_languages = self.language_sets[language_set]
            logger.info(f"Language set changed to: {language_set} - {self.supported_languages}")
            return True
        else:
            logger.error(f"Unknown language set: {language_set}. Available: {list(self.language_sets.keys())}")
            return False
    
    async def stop_recognition(self):
        """Stop recognition and clean up resources"""
        try:
            self.is_active = False
            self.websocket_closed = True  # Mark WebSocket as closed
            
            if self.recognizer:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, self.recognizer.stop_continuous_recognition)
                
            if self.translator:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, self.translator.stop_continuous_recognition)
            
            if self.push_stream:
                self.push_stream.close()
            
            logger.info(f"Azure Speech recognition stopped for session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error stopping recognition: {e}")
    
    async def cleanup(self):
        """Clean up all resources"""
        await self.stop_recognition()
        self.websocket = None
        logger.info(f"Azure Speech session cleanup complete: {self.session_id}")

# Update the active sessions to use Azure Speech
azure_sessions: Dict[str, AzureSpeechSession] = {}

@app.get("/")
async def root():
    return {"message": "Real-Time Speech Translator API - Azure Speech Services"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/azure/supported-languages")
async def get_azure_supported_languages():
    """Get list of languages supported by Azure Speech"""
    return {
        "speech_to_text": [
            {"code": "en-US", "name": "English (US)"},
            {"code": "es-ES", "name": "Spanish (Spain)"},
            {"code": "fr-FR", "name": "French (France)"},
            {"code": "de-DE", "name": "German (Germany)"},
            {"code": "it-IT", "name": "Italian (Italy)"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "hi-IN", "name": "Hindi (India)"},
            {"code": "ja-JP", "name": "Japanese (Japan)"},
            {"code": "ko-KR", "name": "Korean (Korea)"},
            {"code": "zh-CN", "name": "Chinese (Mandarin)"},
            {"code": "ar-SA", "name": "Arabic (Saudi Arabia)"},
            {"code": "ru-RU", "name": "Russian (Russia)"},
            {"code": "nl-NL", "name": "Dutch (Netherlands)"},
            {"code": "sv-SE", "name": "Swedish (Sweden)"}
        ],
        "auto_detection_supported": True,
        "real_time_translation": True
    }

@app.get("/azure/sessions")
async def list_azure_sessions():
    """List active Azure Speech sessions"""
    return {
        "active_sessions": len(azure_sessions),
        "service": "azure_speech",
        "sessions": [
            {
                "session_id": session_id,
                "is_active": session.is_active,
                "source_language": session.source_language,
                "target_language": session.target_language,
                "sample_rate": session.sample_rate
            }
            for session_id, session in azure_sessions.items()
        ]
    }

@app.get("/azure/language-sets")
async def get_language_sets():
    """Get available language sets for auto-detection"""
    # Get language sets from a sample session (they're all the same)
    if azure_sessions:
        sample_session = next(iter(azure_sessions.values()))
        return {
            "available_sets": sample_session.language_sets,
            "current_set": sample_session.supported_languages,
            "note": "Azure auto-detection supports maximum 4 languages at a time"
        }
    else:
        # Return default language sets
        default_sets = {
            "business": ["en-US", "es-ES", "fr-FR", "de-DE"],
            "tech": ["en-US", "zh-CN", "ja-JP", "hi-IN"],
            "european": ["en-GB", "de-DE", "fr-FR", "it-IT"],
            "indian": ["en-IN", "hi-IN", "bn-IN", "te-IN"]
        }
        return {
            "available_sets": default_sets,
            "current_set": ["en-US", "hi-IN", "es-ES", "fr-FR"],
            "note": "Azure auto-detection supports maximum 4 languages at a time"
        }

@app.get("/azure/translator/status")
async def get_translator_status():
    """Get Azure Translator service status - DISABLED for Phase 1 optimization"""
    return {
        "available": False,
        "message": "Azure Translator API disabled for Phase 1 optimization",
        "note": "Using Azure Speech built-in translation for reduced latency"
    }

@app.get("/azure/translator/languages")
async def get_translator_languages():
    """Get supported languages for Azure Translator - DISABLED for Phase 1 optimization"""
    return {
        "languages": [],
        "message": "Azure Translator API disabled for Phase 1 optimization",
        "note": "Using Azure Speech built-in translation for reduced latency"
    }

@app.post("/azure/translator/translate")
async def translate_text(request: dict):
    """Translate text using Azure Translator API - DISABLED for Phase 1 optimization"""
    raise HTTPException(
        status_code=503, 
        detail="Azure Translator API disabled for Phase 1 optimization. Using Azure Speech built-in translation."
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Azure Speech streaming"""
    await websocket.accept()
    session_id = None
    session: AzureSpeechSession = None
    
    try:
        logger.info("WebSocket connection established for Azure Speech")
        
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
        session_id = init_data.get("sessionId", f"azure_session_{uuid.uuid4()}")
        language_pair = init_data.get("language_pair", {"source": "auto", "target": "en"})
        sample_rate = init_data.get("sampleRate", 16000)
        channels = init_data.get("channels", 1)
        
        # Create Azure Speech session
        session = AzureSpeechSession(session_id, sample_rate, channels)
        session.source_language = language_pair.get("source", "auto")
        session.target_language = language_pair.get("target", "en")
        
        # Set language set if specified
        language_set = init_data.get("language_set")
        if language_set:
            session.set_language_set(language_set)
        
        azure_sessions[session_id] = session
        
        # Send session confirmation
        await websocket.send_text(json.dumps({
            "type": "session_confirmed",
            "sessionId": session_id,
            "service": "azure_speech",
            "multilingual_support": True,
            "auto_language_detection": session.source_language == "auto",
            "azure_translator_available": False,  # Disabled for Phase 1 optimization
            "translation_service": "azure_speech_builtin"  # Using built-in translation
        }))
        
        # Start Azure Speech recognition
        recognition_started = await session.start_recognition(websocket)
        
        if recognition_started:
            await websocket.send_text(json.dumps({
                "type": "connection_status",
                "status": "connected",
                "azure_speech_connected": True,
                "multilingual_enabled": True,
                "azure_translator_available": False,  # Disabled for Phase 1 optimization
                "translation_quality": "standard"  # Using Azure Speech built-in translation
            }))
        else:
            await websocket.send_text(json.dumps({
                "type": "connection_status",
                "status": "error",
                "azure_speech_connected": False,
                "message": "Failed to start Azure Speech recognition"
            }))
            return
        
        # Process incoming audio frames
        frame_count = 0
        while session.is_active:
            try:
                # Receive binary audio frame
                frame_data = await websocket.receive_bytes()
                frame_count += 1
                
                # Process with Azure Speech
                result = await session.process_audio_frame(frame_data)
                
                # Send acknowledgment periodically
                if frame_count % 50 == 0:  # Every 50 frames
                    await websocket.send_text(json.dumps({
                        "type": "ack",
                        "seq": frame_count,
                        "azure_status": result["status"]
                    }))
                
                # Log progress
                if frame_count % 100 == 0:
                    logger.info(f"Azure Speech session {session_id}: processed {frame_count} frames")
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for Azure session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error processing audio frame in Azure session {session_id}: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info("Azure Speech WebSocket disconnected")
    except Exception as e:
        logger.error(f"Azure Speech WebSocket error: {e}")
    
    finally:
        # Cleanup
        if session_id and session_id in azure_sessions:
            if session:
                await session.cleanup()
            del azure_sessions[session_id]
            logger.info(f"Azure Speech session {session_id} cleaned up")

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Render provides $PORT)
    port = int(os.getenv("PORT", 8000))
    
    logger.info("Starting Real-Time Speech Translator Backend with Azure Speech Services...")
    logger.info(f"WebSocket endpoint: ws://0.0.0.0:{port}/ws")
    logger.info(f"Azure Speech Region: {AZURE_SPEECH_REGION}")
    logger.info(f"Server will bind to port: {port}")
    
    # Use Render's $PORT environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)
