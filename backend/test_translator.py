"""
Test Azure Translator Integration
================================

This script tests the Azure Translator service to ensure it's working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from azure_translator import translator_service

def test_translator():
    """Test Azure Translator service"""
    print("🧪 Testing Azure Translator Service")
    print("=" * 50)
    
    # Check service status
    print("\n📊 Service Status:")
    status = translator_service.get_service_info()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if not translator_service.is_available():
        print("\n❌ Azure Translator service is not available!")
        print("   Please set AZURE_TRANSLATOR_KEY in your .env file")
        return False
    
    print("\n✅ Azure Translator service is available!")
    
    # Test language detection
    print("\n🔍 Testing Language Detection:")
    test_texts = [
        "Hello, how are you?",
        "नमस्ते, कैसे हो आप?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?"
    ]
    
    for text in test_texts:
        detected = translator_service.detect_language(text)
        print(f"  '{text[:20]}...' -> {detected}")
    
    # Test translations
    print("\n🌐 Testing Translations:")
    test_cases = [
        ("Hello, how are you?", "en", "hi"),
        ("नमस्ते, कैसे हो आप?", "hi", "en"),
        ("Hola, ¿cómo estás?", "es", "en"),
        ("Bonjour, comment allez-vous?", "fr", "en")
    ]
    
    for original, from_lang, to_lang in test_cases:
        result = translator_service.translate_text(original, from_lang, to_lang)
        if result:
            print(f"  {from_lang} -> {to_lang}: '{original[:20]}...' -> '{result['translated_text'][:30]}...'")
        else:
            print(f"  ❌ {from_lang} -> {to_lang}: Failed")
    
    # Test auto-detection
    print("\n🎯 Testing Auto-Detection:")
    auto_test = translator_service.translate_text("Hello world", "auto", "hi")
    if auto_test:
        print(f"  Auto-detect -> Hindi: 'Hello world' -> '{auto_test['translated_text']}'")
        print(f"  Detected language: {auto_test['detectedLanguage']}")
    else:
        print("  ❌ Auto-detection failed")
    
    # Get supported languages
    print("\n📚 Getting Supported Languages:")
    languages = translator_service.get_supported_languages()
    if languages.get("count"):
        print(f"  Total supported languages: {languages['count']}")
        # Show first few languages
        lang_list = list(languages.get("supported_languages", {}).keys())[:10]
        print(f"  Sample languages: {', '.join(lang_list)}")
    else:
        print("  ❌ Failed to get supported languages")
    
    print("\n" + "=" * 50)
    print("🎉 Azure Translator test completed!")
    return True

if __name__ == "__main__":
    try:
        test_translator()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
