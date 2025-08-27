import React from 'react'
import { Languages, ArrowRight } from 'lucide-react'
import { LanguagePair } from '../types'

interface LanguageSelectorProps {
  value: LanguagePair
  onChange: (pair: LanguagePair) => void
  disabled?: boolean
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  value,
  onChange,
  disabled = false
}) => {
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
    { code: 'de', name: 'German', flag: '🇩🇪' },
    { code: 'it', name: 'Italian', flag: '🇮🇹' },
    { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
    { code: 'ru', name: 'Russian', flag: '🇷🇺' },
    { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
    { code: 'ko', name: 'Korean', flag: '🇰🇷' },
    { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
    { code: 'ar', name: 'Arabic', flag: '🇸🇦' }
  ]

  const handleSourceChange = (sourceCode: string) => {
    if (sourceCode !== value.target) {
      onChange({ source: sourceCode, target: value.target })
    }
  }

  const handleTargetChange = (targetCode: string) => {
    if (targetCode !== value.source) {
      onChange({ source: value.source, target: targetCode })
    }
  }

  const swapLanguages = () => {
    onChange({ source: value.target, target: value.source })
  }

  return (
    <div className="space-y-4">
      {/* Language Selection */}
      <div className="flex items-center space-x-3">
        {/* Source Language */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Language
          </label>
          <select
            value={value.source}
            onChange={(e) => handleSourceChange(e.target.value)}
            disabled={disabled}
            className="input-field"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>

        {/* Swap Button */}
        <button
          onClick={swapLanguages}
          disabled={disabled}
          className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Swap languages"
        >
          <ArrowRight className="w-5 h-5" />
        </button>

        {/* Target Language */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Language
          </label>
          <select
            value={value.target}
            onChange={(e) => handleTargetChange(e.target.value)}
            disabled={disabled}
            className="input-field"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Current Selection Display */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center space-x-2 text-sm">
          <Languages className="w-4 h-4 text-blue-600" />
          <span className="text-blue-700 font-medium">Translation Path:</span>
          <span className="text-blue-800">
            {languages.find(l => l.code === value.source)?.name} 
            <ArrowRight className="inline w-4 h-4 mx-2" />
            {languages.find(l => l.code === value.target)?.name}
          </span>
        </div>
      </div>

      {/* Language Info */}
      <div className="text-xs text-gray-600 space-y-1">
        <p>• Source: Language you're speaking in</p>
        <p>• Target: Language for translation</p>
        <p>• AssemblyAI will detect the source language</p>
        <p>• Translation happens in real-time</p>
      </div>
    </div>
  )
}

export default LanguageSelector
