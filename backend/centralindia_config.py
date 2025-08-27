"""
Central India Azure Speech Services Configuration
===============================================

This file contains specific configuration for Central India Azure region.
Use this configuration to ensure optimal performance for users in India.

Endpoint: https://centralindia.api.cognitive.microsoft.com/
Region: centralindia
"""

import os
from typing import Dict

# Central India Azure Speech Services Configuration - Use environment variables for security
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "your-azure-speech-key-here")
AZURE_SPEECH_REGION = "centralindia"  # Fixed to Central India
AZURE_SPEECH_ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"

# Central India specific settings
CENTRAL_INDIA_CONFIG = {
    "region": "centralindia",
    "endpoint": AZURE_SPEECH_ENDPOINT,
    "latency_optimized": True,
    "timezone": "Asia/Kolkata",
    "supported_languages": [
        # Primary languages for India
        {"code": "en-IN", "name": "English (India)", "priority": "high"},
        {"code": "hi-IN", "name": "Hindi (India)", "priority": "high"},
        {"code": "bn-IN", "name": "Bengali (India)", "priority": "high"},
        {"code": "te-IN", "name": "Telugu (India)", "priority": "high"},
        {"code": "mr-IN", "name": "Marathi (India)", "priority": "high"},
        {"code": "ta-IN", "name": "Tamil (India)", "priority": "high"},
        {"code": "gu-IN", "name": "Gujarati (India)", "priority": "high"},
        {"code": "kn-IN", "name": "Kannada (India)", "priority": "high"},
        {"code": "ml-IN", "name": "Malayalam (India)", "priority": "high"},
        {"code": "pa-IN", "name": "Punjabi (India)", "priority": "high"},
        {"code": "ur-IN", "name": "Urdu (India)", "priority": "high"},
        {"code": "or-IN", "name": "Odia (India)", "priority": "high"},
        {"code": "as-IN", "name": "Assamese (India)", "priority": "high"},
        {"code": "ne-IN", "name": "Nepali (India)", "priority": "high"},
        {"code": "sd-IN", "name": "Sindhi (India)", "priority": "high"},
        {"code": "sa-IN", "name": "Sanskrit (India)", "priority": "high"},
        {"code": "ks-IN", "name": "Kashmiri (India)", "priority": "high"},
        {"code": "mni-IN", "name": "Manipuri (India)", "priority": "high"},
        {"code": "doi-IN", "name": "Dogri (India)", "priority": "high"},
        {"code": "bho-IN", "name": "Bhojpuri (India)", "priority": "high"},
        {"code": "sat-IN", "name": "Santali (India)", "priority": "high"},
        {"code": "kok-IN", "name": "Konkani (India)", "priority": "high"},
        {"code": "brx-IN", "name": "Bodo (India)", "priority": "high"},
        # International languages
        {"code": "en-US", "name": "English (US)", "priority": "medium"},
        {"code": "es-ES", "name": "Spanish (Spain)", "priority": "medium"},
        {"code": "fr-FR", "name": "French (France)", "priority": "medium"},
        {"code": "de-DE", "name": "German (Germany)", "priority": "medium"},
        {"code": "it-IT", "name": "Italian (Italy)", "priority": "medium"},
        {"code": "pt-BR", "name": "Portuguese (Brazil)", "priority": "medium"},
        {"code": "ja-JP", "name": "Japanese (Japan)", "priority": "medium"},
        {"code": "ko-KR", "name": "Korean (Korea)", "priority": "medium"},
        {"code": "zh-CN", "name": "Chinese (Mandarin)", "priority": "medium"},
        {"code": "ar-SA", "name": "Arabic (Saudi Arabia)", "priority": "medium"},
        {"code": "ru-RU", "name": "Russian (Russia)", "priority": "medium"}
    ],
    "translation_targets": [
        # Primary targets for India
        {"code": "en", "name": "English", "priority": "high"},
        {"code": "hi", "name": "Hindi", "priority": "high"},
        {"code": "bn", "name": "Bengali", "priority": "high"},
        {"code": "te", "name": "Telugu", "priority": "high"},
        {"code": "mr", "name": "Marathi", "priority": "high"},
        {"code": "ta", "name": "Tamil", "priority": "high"},
        {"code": "gu", "name": "Gujarati", "priority": "high"},
        {"code": "kn", "name": "Kannada", "priority": "high"},
        {"code": "ml", "name": "Malayalam", "priority": "high"},
        {"code": "pa", "name": "Punjabi", "priority": "high"},
        {"code": "ur", "name": "Urdu", "priority": "high"},
        {"code": "or", "name": "Odia", "priority": "high"},
        {"code": "as", "name": "Assamese", "priority": "high"},
        {"code": "ne", "name": "Nepali", "priority": "high"},
        {"code": "sd", "name": "Sindhi", "priority": "high"},
        {"code": "sa", "name": "Sanskrit", "priority": "high"},
        {"code": "ks", "name": "Kashmiri", "priority": "high"},
        {"code": "mni", "name": "Manipuri", "priority": "high"},
        {"code": "doi", "name": "Dogri", "priority": "high"},
        {"code": "bho", "name": "Bhojpuri", "priority": "high"},
        {"code": "sat", "name": "Santali", "priority": "high"},
        {"code": "kok", "name": "Konkani", "priority": "high"},
        {"code": "brx", "name": "Bodo", "priority": "high"},
        # International targets
        {"code": "es", "name": "Spanish", "priority": "medium"},
        {"code": "fr", "name": "French", "priority": "medium"},
        {"code": "de", "name": "German", "priority": "medium"},
        {"code": "it", "name": "Italian", "priority": "medium"},
        {"code": "pt", "name": "Portuguese", "priority": "medium"},
        {"code": "ja", "name": "Japanese", "priority": "medium"},
        {"code": "ko", "name": "Korean", "priority": "medium"},
        {"code": "zh", "name": "Chinese", "priority": "medium"},
        {"code": "ar", "name": "Arabic", "priority": "medium"},
        {"code": "ru", "name": "Russian", "priority": "medium"}
    ]
}

# Audio Configuration optimized for Central India
AUDIO_CONFIG = {
    "sample_rate": 16000,        # 16kHz sample rate
    "channels": 1,               # Mono channel
    "frame_duration_ms": 128,    # 128ms frames
    "encoding": "pcm_s16le",     # 16-bit signed little-endian PCM
    "format": "riff-16khz-16bit-mono-pcm",
    "buffer_size": 2048,         # Optimized for Central India latency
    "network_optimization": True # Enable network optimization for India
}

# Performance Configuration for Central India
PERFORMANCE_CONFIG = {
    "continuous_recognition": True,
    "auto_language_detection": True,
    "real_time_translation": True,
    "max_alternatives": 1,
    "profanity_filter": False,
    "word_level_timestamps": False,
    "india_optimized": True,     # Enable India-specific optimizations
    "regional_latency": "centralindia"  # Optimize for Central India
}

def validate_central_india_config() -> Dict[str, bool]:
    """Validate Central India Azure Speech Services configuration"""
    validation_results = {
        "azure_key_configured": AZURE_SPEECH_KEY != "your-azure-speech-key-here",
        "azure_region_valid": AZURE_SPEECH_REGION == "centralindia",
        "azure_key_length": len(AZURE_SPEECH_KEY) >= 32 if AZURE_SPEECH_KEY != "your-azure-speech-key-here" else False,
        "central_india_endpoint": AZURE_SPEECH_ENDPOINT == "https://centralindia.api.cognitive.microsoft.com/",
        "india_languages_configured": len([lang for lang in CENTRAL_INDIA_CONFIG["supported_languages"] if lang["priority"] == "high"]) >= 20
    }
    
    return validation_results

def get_central_india_summary() -> Dict[str, any]:
    """Get Central India configuration summary"""
    return {
        "azure_region": AZURE_SPEECH_REGION,
        "azure_endpoint": AZURE_SPEECH_ENDPOINT,
        "supported_languages_count": len(CENTRAL_INDIA_CONFIG["supported_languages"]),
        "india_languages_count": len([lang for lang in CENTRAL_INDIA_CONFIG["supported_languages"] if lang["priority"] == "high"]),
        "translation_targets_count": len(CENTRAL_INDIA_CONFIG["translation_targets"]),
        "india_translation_targets": len([lang for lang in CENTRAL_INDIA_CONFIG["translation_targets"] if lang["priority"] == "high"]),
        "audio_sample_rate": AUDIO_CONFIG["sample_rate"],
        "auto_language_detection": PERFORMANCE_CONFIG["auto_language_detection"],
        "real_time_translation": PERFORMANCE_CONFIG["real_time_translation"],
        "india_optimized": PERFORMANCE_CONFIG["india_optimized"]
    }

if __name__ == "__main__":
    # Central India configuration validation and display
    print("Central India Azure Speech Services Configuration")
    print("===============================================")
    print(f"Region: {AZURE_SPEECH_REGION}")
    print(f"Endpoint: {AZURE_SPEECH_ENDPOINT}")
    print(f"Supported Languages: {len(CENTRAL_INDIA_CONFIG['supported_languages'])}")
    print(f"India Languages: {len([lang for lang in CENTRAL_INDIA_CONFIG['supported_languages'] if lang['priority'] == 'high'])}")
    print(f"Translation Targets: {len(CENTRAL_INDIA_CONFIG['translation_targets'])}")
    print(f"India Translation Targets: {len([lang for lang in CENTRAL_INDIA_CONFIG['translation_targets'] if lang['priority'] == 'high'])}")
    print(f"Audio Sample Rate: {AUDIO_CONFIG['sample_rate']}Hz")
    print(f"India Optimized: {PERFORMANCE_CONFIG['india_optimized']}")
    
    validation = validate_central_india_config()
    print("\nCentral India Configuration Validation:")
    for key, value in validation.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    if not validation["azure_key_configured"]:
        print("\n⚠️  Please configure AZURE_SPEECH_KEY in your environment variables")
        print("   or create a .env file with your Azure Speech Services key")
    
    if not validation["azure_region_valid"]:
        print(f"\n⚠️  Region must be 'centralindia' for optimal performance in India")
    
    if validation["india_languages_configured"]:
        print(f"\n✅ Central India configuration optimized for {validation['india_languages_configured']} Indian languages")
    
    print(f"\n🌍 Central India endpoint: {AZURE_SPEECH_ENDPOINT}")
    print("   This endpoint provides optimal performance for users in India")
