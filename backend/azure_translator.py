"""
Azure Translator Service
=======================

This module provides translation services using Azure Translator API.
It offers better translation quality and more language options than the built-in Azure Speech translation.
"""

import os
import requests
import uuid
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AzureTranslatorService:
    """Azure Translator API service for high-quality translations"""
    
    def __init__(self):
        # Use environment variables for security
        self.key = os.getenv("AZURE_TRANSLATOR_KEY")
        self.endpoint = "https://api.cognitive.microsofttranslator.com"
        self.location = os.getenv("AZURE_TRANSLATOR_LOCATION", "centralindia")
        
        if not self.key:
            logger.warning("AZURE_TRANSLATOR_KEY not set. Translation will fall back to Azure Speech built-in translation.")
            self.available = False
        else:
            self.available = True
            logger.info(f"Azure Translator service initialized for region: {self.location}")
    
    def translate_text(self, text: str, from_lang: str, to_lang: str) -> Optional[Dict]:
        """
        Translate text using Azure Translator API
        
        Args:
            text: Text to translate
            from_lang: Source language code (e.g., 'en', 'hi', 'auto')
            to_lang: Target language code (e.g., 'en', 'hi', 'fr')
        
        Returns:
            Translation result or None if failed
        """
        if not self.available or not text.strip():
            return None
        
        try:
            # Handle auto-detection
            if from_lang == 'auto':
                # Try to detect language first
                detected_lang = self.detect_language(text)
                if detected_lang:
                    from_lang = detected_lang
                else:
                    from_lang = 'en'  # Default to English if detection fails
            
            # Don't translate if source and target are the same
            if from_lang == to_lang:
                return {
                    "translated_text": text,
                    "detectedLanguage": from_lang,
                    "confidence": 1.0,
                    "service": "azure_translator",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare translation request
            path = '/translate'
            constructed_url = self.endpoint + path
            
            params = {
                'api-version': '3.0',
                'from': from_lang,
                'to': to_lang
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                'Ocp-Apim-Subscription-Region': self.location,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            body = [{
                'text': text
            }]
            
            # Make translation request
            response = requests.post(constructed_url, params=params, headers=headers, json=body)
            response.raise_for_status()
            
            translation_result = response.json()
            
            if translation_result and len(translation_result) > 0:
                result = translation_result[0]
                translations = result.get('translations', [])
                
                if translations and len(translations) > 0:
                    translated_text = translations[0].get('text', text)
                    
                    return {
                        "translated_text": translated_text,
                        "detectedLanguage": from_lang,
                        "confidence": 0.95,  # Azure Translator typically has high confidence
                        "service": "azure_translator",
                        "timestamp": datetime.now().isoformat(),
                        "original_text": text,
                        "source_language": from_lang,
                        "target_language": to_lang
                    }
            
            logger.warning(f"Translation failed for text: {text[:50]}...")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Azure Translator API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text
        
        Args:
            text: Text to detect language for
        
        Returns:
            Detected language code or None if failed
        """
        if not self.available or not text.strip():
            return None
        
        try:
            path = '/detect'
            constructed_url = self.endpoint + path
            
            params = {
                'api-version': '3.0'
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                'Ocp-Apim-Subscription-Region': self.location,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            body = [{
                'text': text
            }]
            
            response = requests.post(constructed_url, params=params, headers=headers, json=body)
            response.raise_for_status()
            
            detection_result = response.json()
            
            if detection_result and len(detection_result) > 0:
                result = detection_result[0]
                detected_lang = result.get('language')
                confidence = result.get('score', 0.0)
                
                if detected_lang and confidence > 0.5:  # Only return if confidence is reasonable
                    logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
                    return detected_lang
            
            return None
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages for translation"""
        try:
            path = '/languages'
            constructed_url = self.endpoint + path
            
            params = {
                'api-version': '3.0',
                'scope': 'translation'
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                'Ocp-Apim-Subscription-Region': self.location,
                'Content-type': 'application/json'
            }
            
            response = requests.get(constructed_url, params=params, headers=headers)
            response.raise_for_status()
            
            languages = response.json()
            return {
                "supported_languages": languages,
                "count": len(languages) if languages else 0,
                "service": "azure_translator"
            }
            
        except Exception as e:
            logger.error(f"Failed to get supported languages: {e}")
            return {"supported_languages": {}, "count": 0, "error": str(e)}
    
    def is_available(self) -> bool:
        """Check if Azure Translator service is available"""
        return self.available
    
    def get_service_info(self) -> Dict:
        """Get service information and status"""
        return {
            "service": "azure_translator",
            "available": self.available,
            "endpoint": self.endpoint,
            "location": self.location,
            "key_configured": bool(self.key)
        }

# Global instance
translator_service = AzureTranslatorService()
