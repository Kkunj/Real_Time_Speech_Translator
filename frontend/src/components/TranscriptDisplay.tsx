import React, { useEffect, useState } from 'react'
import { Languages, Mic, MicOff } from 'lucide-react'
import { TranscriptEntry, ConnectionState, LanguagePair } from '../types'

interface TranscriptDisplayProps {
  transcripts: TranscriptEntry[]
  connectionState: ConnectionState
  languagePair: LanguagePair
}

const TranscriptDisplay: React.FC<TranscriptDisplayProps> = ({
  transcripts,
  connectionState,
  languagePair
}) => {
  const [currentPartial, setCurrentPartial] = useState<string>('')
  const [lastLanguagePair, setLastLanguagePair] = useState<LanguagePair>(languagePair)

  // Track language pair changes
  useEffect(() => {
    if (languagePair.target !== lastLanguagePair.target) {
      setLastLanguagePair(languagePair)
      // Clear current partial when language changes to avoid confusion
      setCurrentPartial('')
    }
  }, [languagePair, lastLanguagePair])

  // Update current partial transcript with word limit for readability
  useEffect(() => {
    const partials = transcripts.filter(t => t.type === 'partial')
    if (partials.length > 0) {
      const latestPartial = partials[partials.length - 1]
      const originalText = latestPartial.original
      
      // Limit to 50 words for better readability
      const words = originalText.split(' ')
      if (words.length > 50) {
        setCurrentPartial(words.slice(-50).join(' ') + '...')
      } else {
        setCurrentPartial(originalText)
      }
    }
  }, [transcripts])

  // Get current translated text - only show actual translations, not original text
  const getCurrentTranslatedPartial = () => {
    if (currentPartial) {
      // Try to get the latest translation from partial transcripts
      const partials = transcripts.filter(t => t.type === 'partial')
      if (partials.length > 0) {
        const latestPartial = partials[partials.length - 1]
        // Only return if we have an actual translation, not the original text
        if (latestPartial.translated && latestPartial.translated !== latestPartial.original) {
          // Limit to 50 words for readability
          const words = latestPartial.translated.split(' ')
          if (words.length > 50) {
            return words.slice(-50).join(' ') + '...'
          }
          return latestPartial.translated
        }
      }
      
      // Also check final transcripts for translations
      const finalTranscripts = transcripts.filter(t => t.type === 'final')
      if (finalTranscripts.length > 0) {
        const latestFinal = finalTranscripts[finalTranscripts.length - 1]
        if (latestFinal.translated && latestFinal.translated !== latestFinal.original) {
          // Limit to 50 words for readability
          const words = latestFinal.translated.split(' ')
          if (words.length > 50) {
            return words.slice(-50).join(' ') + '...'
          }
          return latestFinal.translated
        }
      }
      
      // If no translation available, return empty string
      return ''
    }
    return ''
  }

  // Get current detected language
  const getCurrentDetectedLanguage = () => {
    const partials = transcripts.filter(t => t.type === 'partial')
    if (partials.length > 0) {
      const latestPartial = partials[partials.length - 1]
      return latestPartial.detectedLanguage || 'unknown'
    }
    return 'unknown'
  }

  // Get word count for current text
  const getWordCount = (text: string) => {
    if (!text) return 0
    return text.split(' ').filter(word => word.trim().length > 0).length
  }

  // Get user-friendly language name
  const getLanguageName = (languageCode: string) => {
    const languageNames: { [key: string]: string } = {
      'en': 'English',
      'hi': 'Hindi',
      'te': 'Telugu',
      'ta': 'Tamil',
      'bn': 'Bengali',
      'gu': 'Gujarati',
      'kn': 'Kannada',
      'ml': 'Malayalam',
      'mr': 'Marathi',
      'pa': 'Punjabi',
      'ur': 'Urdu',
      'es': 'Spanish',
      'fr': 'French',
      'de': 'German',
      'it': 'Italian',
      'pt': 'Portuguese',
      'ru': 'Russian',
      'ja': 'Japanese',
      'ko': 'Korean',
      'zh': 'Chinese',
      'ar': 'Arabic'
    }
    return languageNames[languageCode] || languageCode.toUpperCase()
  }



  if (connectionState === 'disconnected') {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <MicOff className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">No Active Session</h3>
          <p className="text-sm">Start capturing audio to see live transcripts</p>
        </div>
      </div>
    )
  }



  return (
    <div className="h-full flex flex-col">
      {/* Simple Header */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-700">Live Speech Translation</h3>
          <p className="text-sm text-gray-500">
            Auto-detect → {getLanguageName(languagePair.target)} • Real-time captions and translations
          </p>
        </div>
      </div>

      {/* Live Transcripts Container - Always show both boxes when there's content */}
      <div className="mb-4 space-y-3">
        {/* Original Language Box */}
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <div className={`w-3 h-3 rounded-full animate-pulse ${currentPartial ? 'bg-blue-500' : 'bg-gray-400'}`} />
            <Mic className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">Original Language</span>
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              🌍 {getCurrentDetectedLanguage()}
            </span>
            {currentPartial && (
              <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full">
                🔊 Active
              </span>
            )}
          </div>
          <p className="text-blue-900 text-xl font-medium leading-relaxed">
            {currentPartial || "Waiting for speech..."}
          </p>
          <div className="mt-2 text-xs text-blue-600">
            {currentPartial ? `Speaking in real-time... (${getWordCount(currentPartial)} words)` : "Ready to capture"}
          </div>
        </div>

        {/* Translation Box */}
        <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <div className={`w-3 h-3 rounded-full animate-pulse ${getCurrentTranslatedPartial() ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <Languages className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-800">{getLanguageName(languagePair.target)} Translation</span>
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
              🎯 {getLanguageName(languagePair.target)}
            </span>
            {getCurrentTranslatedPartial() && (
              <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">
                ✓ Live
              </span>
            )}
            {languagePair.target !== lastLanguagePair.target && (
              <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full animate-pulse">
                🔄 New
              </span>
            )}
          </div>
          <p className="text-green-900 text-xl font-medium leading-relaxed">
            {getCurrentTranslatedPartial() || "Waiting for translation..."}
          </p>
          <div className="mt-2 text-xs text-green-600">
            {getCurrentTranslatedPartial() ? `Translating in real-time... (${getWordCount(getCurrentTranslatedPartial())} words)` : "Processing speech..."}
          </div>
        </div>
      </div>

      {/* Simple Status Footer */}
      <div className="mt-auto pt-4 border-t border-gray-200">
        <div className="text-center text-xs text-gray-500">
          <span className="flex items-center justify-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${connectionState === 'connected' ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <span>
              {connectionState === 'connected' ? 'Live streaming' : 'Connecting...'}
            </span>
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${connectionState === 'connected' ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <span>
              {connectionState === 'connected' ? 'Live streaming' : 'Connecting...'}
            </span>
          </span>
          <span>
            Last update: {transcripts.length > 0 ? 'Recent' : 'Never'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default TranscriptDisplay
