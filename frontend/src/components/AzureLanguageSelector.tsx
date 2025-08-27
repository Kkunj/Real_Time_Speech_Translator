import React from 'react'
import { LanguagePair } from '../types'

interface AzureLanguageSelectorProps {
  value: LanguagePair
  onChange: (pair: LanguagePair) => void
  disabled?: boolean
}

const AzureLanguageSelector: React.FC<AzureLanguageSelectorProps> = ({
  value,
  onChange,
  disabled = false
}) => {
  // Only show languages that are supported for auto-detection (Azure limitation: 4 languages max)
  const azureLanguages = [
    { code: 'auto', name: 'Auto-Detect (Multilingual)' },
    { code: 'en-US', name: 'English (US)' },
    { code: 'hi-IN', name: 'Hindi (India)' },
    { code: 'es-ES', name: 'Spanish (Spain)' },
    { code: 'fr-FR', name: 'French (France)' }
  ]

  const translationTargets = [
    // Indian Languages (High Priority for Central India)
    { code: 'en', name: 'English', priority: 'high' },
    { code: 'hi', name: 'Hindi', priority: 'high' },
    { code: 'bn', name: 'Bengali', priority: 'high' },
    { code: 'te', name: 'Telugu', priority: 'high' },
    { code: 'mr', name: 'Marathi', priority: 'high' },
    { code: 'ta', name: 'Tamil', priority: 'high' },
    { code: 'gu', name: 'Gujarati', priority: 'high' },
    { code: 'kn', name: 'Kannada', priority: 'high' },
    { code: 'ml', name: 'Malayalam', priority: 'high' },
    { code: 'pa', name: 'Punjabi', priority: 'high' },
    { code: 'ur', name: 'Urdu', priority: 'high' },
    { code: 'or', name: 'Odia', priority: 'high' },
    { code: 'as', name: 'Assamese', priority: 'high' },
    { code: 'ne', name: 'Nepali', priority: 'high' },
    { code: 'sd', name: 'Sindhi', priority: 'high' },
    { code: 'sa', name: 'Sanskrit', priority: 'high' },
    { code: 'ks', name: 'Kashmiri', priority: 'high' },
    { code: 'mni', name: 'Manipuri', priority: 'high' },
    { code: 'doi', name: 'Dogri', priority: 'high' },
    { code: 'bho', name: 'Bhojpuri', priority: 'high' },
    { code: 'sat', name: 'Santali', priority: 'high' },
    { code: 'kok', name: 'Konkani', priority: 'high' },
    { code: 'brx', name: 'Bodo', priority: 'high' },
    // International Languages
    { code: 'es', name: 'Spanish', priority: 'medium' },
    { code: 'fr', name: 'French', priority: 'medium' },
    { code: 'de', name: 'German', priority: 'medium' },
    { code: 'it', name: 'Italian', priority: 'medium' },
    { code: 'pt', name: 'Portuguese', priority: 'medium' },
    { code: 'ja', name: 'Japanese', priority: 'medium' },
    { code: 'ko', name: 'Korean', priority: 'medium' },
    { code: 'zh', name: 'Chinese', priority: 'medium' },
    { code: 'ar', name: 'Arabic', priority: 'medium' },
    { code: 'ru', name: 'Russian', priority: 'medium' }
  ]

  return (
    <div className="space-y-6">
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-base text-blue-800 font-medium">
          🎯 Azure Speech Services - Central India Region
        </p>
        <p className="text-sm text-blue-600 mt-2">
          🌍 Optimized for users in India with 23 Indian languages
        </p>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-base font-semibold text-gray-700 mb-3">
            Source Language (Speech Recognition)
          </label>
          <select
            value={value.source}
            onChange={(e) => onChange({ ...value, source: e.target.value })}
            disabled={disabled}
            className="input-field w-full text-base p-3"
          >
            {azureLanguages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
          {value.source === 'auto' && (
            <p className="text-sm text-green-600 mt-2 font-medium">
              ✨ Azure will automatically detect the spoken language (supports 4 languages at a time)
            </p>
          )}
        </div>

        <div>
          <label className="block text-base font-semibold text-gray-700 mb-3">
            Target Language (Translation)
          </label>
          <select
            value={value.target}
            onChange={(e) => onChange({ ...value, target: e.target.value })}
            disabled={disabled}
            className="input-field w-full text-base p-3"
          >
            {translationTargets.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Current Selection Display */}
      <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
        <div className="flex items-center space-x-2 text-base">
          <span className="text-green-700 font-semibold">Current Configuration:</span>
          <span className="text-green-800 font-medium">
            {value.source === 'auto' ? 'Auto-Detect' : azureLanguages.find(l => l.code === value.source)?.name} 
            <span className="mx-2">→</span>
            {translationTargets.find(l => l.code === value.target)?.name}
          </span>
        </div>
        {value.source === 'auto' && (
          <p className="text-sm text-green-600 mt-2">
            🌍 Auto-detection supports: English, Hindi, Spanish, French
          </p>
        )}
      </div>
    </div>
  )
}

export default AzureLanguageSelector
