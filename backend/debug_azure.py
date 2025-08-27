"""
Debug Azure Speech Services Connection
====================================

This script tests Azure Speech Services step by step to identify the issue.
"""

import os
import asyncio
import azure.cognitiveservices.speech as speechsdk
import azure.cognitiveservices.speech.translation as speech_translation
from azure.cognitiveservices.speech import AutoDetectSourceLanguageConfig
from concurrent.futures import ThreadPoolExecutor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_azure_connection():
    """Test Azure Speech Services connection step by step"""
    
    print("🔍 Testing Azure Speech Services Connection Step by Step")
    print("=" * 60)
    
    # Get environment variables
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    
    print(f"✅ Environment Variables:")
    print(f"   Key: {key[:10]}...{key[-4:] if key else 'NOT_SET'}")
    print(f"   Region: {region}")
    print()
    
    if not key or not region:
        print("❌ Environment variables not set properly")
        return False
    
    try:
        # Step 1: Test basic SpeechConfig
        print("🔧 Step 1: Creating SpeechConfig...")
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        print("   ✅ SpeechConfig created successfully")
        
        # Step 2: Test properties (skipping unsupported properties)
        print("🔧 Step 2: Testing configuration...")
        # Note: These properties are not available in Azure Speech SDK 1.45.0
        # Continuous recognition is enabled by default
        # Audio format is handled automatically by the SDK
        print("   ✅ Configuration ready (properties not needed in this SDK version)")
        
        # Step 3: Test TranslationConfig
        print("🔧 Step 3: Creating SpeechTranslationConfig...")
        translation_config = speech_translation.SpeechTranslationConfig(
            subscription=key, region=region
        )
        print("   ✅ SpeechTranslationConfig created successfully")
        
        # Step 4: Test target language
        print("🔧 Step 4: Adding target language...")
        translation_config.add_target_language("en")
        print("   ✅ Target language added successfully")
        
        # Step 5: Test supported languages
        print("🔧 Step 5: Testing supported languages...")
        supported_languages = [
            "en-US", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "hi-IN",
            "ja-JP", "ko-KR", "zh-CN", "ar-SA", "ru-RU", "nl-NL", "sv-SE"
        ]
        
        print(f"   Testing {len(supported_languages)} languages...")
        auto_detect_config = AutoDetectSourceLanguageConfig(languages=supported_languages)
        print("   ✅ AutoDetectSourceLanguageConfig created successfully")
        
        # Step 6: Test audio stream
        print("🔧 Step 6: Creating audio stream...")
        push_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
        print("   ✅ Audio stream created successfully")
        
        # Step 7: Test TranslationRecognizer creation
        print("🔧 Step 7: Creating TranslationRecognizer...")
        translator = speech_translation.TranslationRecognizer(
            translation_config=translation_config,
            audio_config=audio_config,
            auto_detect_source_language_config=auto_detect_config
        )
        print("   ✅ TranslationRecognizer created successfully")
        
        # Step 8: Test event handlers
        print("🔧 Step 8: Setting up event handlers...")
        
        def on_recognizing(evt):
            print(f"   🔄 Recognizing: {evt.result.text}")
        
        def on_recognized(evt):
            print(f"   ✅ Recognized: {evt.result.text}")
        
        def on_canceled(evt):
            print(f"   ❌ Canceled: {evt.reason}")
            if evt.reason == speechsdk.CancellationReason.Error:
                print(f"      Error: {evt.error_details}")
        
        translator.recognizing.connect(on_recognizing)
        translator.recognized.connect(on_recognized)
        translator.canceled.connect(on_canceled)
        print("   ✅ Event handlers connected successfully")
        
        # Step 9: Test continuous recognition start
        print("🔧 Step 9: Starting continuous recognition...")
        
        def start_recognition():
            try:
                translator.start_continuous_recognition()
                print("   ✅ Continuous recognition started successfully")
                return True
            except Exception as e:
                print(f"   ❌ Failed to start continuous recognition: {e}")
                return False
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, start_recognition)
        
        if result:
            print("   ✅ All tests passed!")
            
            # Stop recognition
            print("🔧 Step 10: Stopping recognition...")
            def stop_recognition():
                try:
                    translator.stop_continuous_recognition()
                    print("   ✅ Recognition stopped successfully")
                except Exception as e:
                    print(f"   ❌ Error stopping recognition: {e}")
            
            await loop.run_in_executor(executor, stop_recognition)
            
            return True
        else:
            print("   ❌ Continuous recognition test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_azure_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All Azure Speech Services tests passed!")
        print("   Your configuration is working correctly.")
    else:
        print("❌ Some tests failed.")
        print("   Check the error messages above for details.")
    
    print("\n📚 Next steps:")
    print("   1. If all tests passed, try running main.py again")
    print("   2. If tests failed, check the specific error messages")
    print("   3. Verify your Azure Speech Services subscription is active")

if __name__ == "__main__":
    asyncio.run(main())
