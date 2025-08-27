"""
Azure Speech Services Configuration
=================================

This file contains configuration settings for Azure Speech Services.
Copy this file to azure_config_local.py and update with your actual values.

Required:
- AZURE_SPEECH_KEY: Your Azure Speech Services subscription key
- AZURE_SPEECH_REGION: Your Azure Speech Services region

Optional:
- Custom language configurations
- Audio format settings
- Performance tuning parameters
"""

import os
from typing import List, Dict

# Azure Speech Services Configuration - Use environment variables for security
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "your-azure-speech-key-here")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "centralindia")  # Central India region

# Supported Azure Speech Regions
AZURE_REGIONS = [
    "eastus",           # East US
    "eastus2",          # East US 2
    "southcentralus",   # South Central US
    "westus2",          # West US 2
    "westeurope",       # West Europe
    "northeurope",      # North Europe
    "eastasia",         # East Asia
    "southeastasia",    # Southeast Asia
    "australiaeast",    # Australia East
    "brazilsouth",      # Brazil South
    "canadacentral",    # Canada Central
    "centralindia",     # Central India
    "japaneast",        # Japan East
    "koreacentral",     # Korea Central
    "uksouth",          # UK South
    "francecentral",    # France Central
    "germanywestcentral", # Germany West Central
    "switzerlandnorth", # Switzerland North
    "uaenorth",         # UAE North
    "southafricanorth"  # South Africa North
]

# Supported Languages for Speech Recognition
SUPPORTED_LANGUAGES = [
    {"code": "en-US", "name": "English (US)", "region": "United States"},
    {"code": "es-ES", "name": "Spanish (Spain)", "region": "Spain"},
    {"code": "fr-FR", "name": "French (France)", "region": "France"},
    {"code": "de-DE", "name": "German (Germany)", "region": "Germany"},
    {"code": "it-IT", "name": "Italian (Italy)", "region": "Italy"},
    {"code": "pt-BR", "name": "Portuguese (Brazil)", "region": "Brazil"},
    {"code": "hi-IN", "name": "Hindi (India)", "region": "India"},
    {"code": "ja-JP", "name": "Japanese (Japan)", "region": "Japan"},
    {"code": "ko-KR", "name": "Korean (Korea)", "region": "Korea"},
    {"code": "zh-CN", "name": "Chinese (Mandarin)", "region": "China"},
    {"code": "ar-SA", "name": "Arabic (Saudi Arabia)", "region": "Saudi Arabia"},
    {"code": "ru-RU", "name": "Russian (Russia)", "region": "Russia"},
    {"code": "nl-NL", "name": "Dutch (Netherlands)", "region": "Netherlands"},
    {"code": "sv-SE", "name": "Swedish (Sweden)", "region": "Sweden"},
    {"code": "da-DK", "name": "Danish (Denmark)", "region": "Denmark"},
    {"code": "no-NO", "name": "Norwegian (Norway)", "region": "Norway"},
    {"code": "fi-FI", "name": "Finnish (Finland)", "region": "Finland"},
    {"code": "pl-PL", "name": "Polish (Poland)", "region": "Poland"},
    {"code": "tr-TR", "name": "Turkish (Turkey)", "region": "Turkey"},
    {"code": "he-IL", "name": "Hebrew (Israel)", "region": "Israel"},
    {"code": "th-TH", "name": "Thai (Thailand)", "region": "Thailand"},
    {"code": "vi-VN", "name": "Vietnamese (Vietnam)", "region": "Vietnam"}
]

# Translation Target Languages (simplified codes)
TRANSLATION_TARGETS = [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "it", "name": "Italian"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "hi", "name": "Hindi"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ar", "name": "Arabic"},
    {"code": "ru", "name": "Russian"},
    {"code": "nl", "name": "Dutch"},
    {"code": "sv", "name": "Swedish"},
    {"code": "da", "name": "Danish"},
    {"code": "no", "name": "Norwegian"},
    {"code": "fi", "name": "Finnish"},
    {"code": "pl", "name": "Polish"},
    {"code": "tr", "name": "Turkish"},
    {"code": "he", "name": "Hebrew"},
    {"code": "th", "name": "Thai"},
    {"code": "vi", "name": "Vietnamese"}
]

# Audio Configuration
AUDIO_CONFIG = {
    "sample_rate": 16000,        # 16kHz sample rate
    "channels": 1,               # Mono channel
    "frame_duration_ms": 128,    # 128ms frames
    "encoding": "pcm_s16le",     # 16-bit signed little-endian PCM
    "format": "riff-16khz-16bit-mono-pcm"
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "continuous_recognition": True,
    "auto_language_detection": True,
    "real_time_translation": True,
    "max_alternatives": 1,
    "profanity_filter": False,
    "word_level_timestamps": False
}

def validate_config() -> Dict[str, bool]:
    """Validate Azure Speech Services configuration"""
    validation_results = {
        "azure_key_configured": AZURE_SPEECH_KEY != "your-azure-speech-key-here",
        "azure_region_valid": AZURE_SPEECH_REGION in AZURE_REGIONS,
        "azure_key_length": len(AZURE_SPEECH_KEY) >= 32 if AZURE_SPEECH_KEY != "your-azure-speech-key-here" else False
    }
    
    return validation_results

def get_config_summary() -> Dict[str, any]:
    """Get configuration summary for logging"""
    return {
        "azure_region": AZURE_SPEECH_REGION,
        "supported_languages_count": len(SUPPORTED_LANGUAGES),
        "translation_targets_count": len(TRANSLATION_TARGETS),
        "audio_sample_rate": AUDIO_CONFIG["sample_rate"],
        "auto_language_detection": PERFORMANCE_CONFIG["auto_language_detection"],
        "real_time_translation": PERFORMANCE_CONFIG["real_time_translation"]
    }

if __name__ == "__main__":
    # Configuration validation and display
    print("Azure Speech Services Configuration")
    print("==================================")
    print(f"Region: {AZURE_SPEECH_REGION}")
    print(f"Supported Languages: {len(SUPPORTED_LANGUAGES)}")
    print(f"Translation Targets: {len(TRANSLATION_TARGETS)}")
    print(f"Audio Sample Rate: {AUDIO_CONFIG['sample_rate']}Hz")
    
    validation = validate_config()
    print("\nConfiguration Validation:")
    for key, value in validation.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    if not validation["azure_key_configured"]:
        print("\n⚠️  Please configure AZURE_SPEECH_KEY in your environment variables")
        print("   or create a .env file with your Azure Speech Services key")
    
    if not validation["azure_region_valid"]:
        print(f"\n⚠️  Invalid region '{AZURE_SPEECH_REGION}'. Valid regions:")
        for region in AZURE_REGIONS[:5]:  # Show first 5
            print(f"     - {region}")
        print("     ... and more")
