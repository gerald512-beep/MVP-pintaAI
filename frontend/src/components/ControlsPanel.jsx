import React from 'react'
import CustomizedTab from './CustomizedTab'
import { t } from '../i18n/translations'

export default function ControlsPanel({
  age, setAge,
  topic, setTopic,
  imageFile, setImageFile,
  imagePreviewUrl, setImagePreviewUrl,
  customConfig, setCustomConfig,
  onGenerate,
  isLoading,
}) {
  const canGenerate = age && topic && imageFile && !isLoading

  return (
    <div className="w-80 flex-shrink-0 flex flex-col gap-6 p-6 bg-white border-r border-gray-200 h-full overflow-y-auto">
      <div>
        <h1 className="text-xl font-bold text-gray-900">{t.appTitle}</h1>
        <p className="text-sm text-gray-500 mt-0.5">{t.appSubtitle}</p>
      </div>

      <CustomizedTab
        age={age}
        setAge={setAge}
        topic={topic}
        setTopic={setTopic}
        imageFile={imageFile}
        setImageFile={setImageFile}
        imagePreviewUrl={imagePreviewUrl}
        setImagePreviewUrl={setImagePreviewUrl}
        customConfig={customConfig}
        setCustomConfig={setCustomConfig}
      />

      <div className="mt-auto pt-4">
        <button
          onClick={onGenerate}
          disabled={!canGenerate}
          className={`w-full py-3 px-4 rounded-lg font-semibold text-sm transition-colors flex items-center justify-center gap-2 ${
            canGenerate
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              {t.generating}
            </>
          ) : (
            t.generate
          )}
        </button>

        {!canGenerate && !isLoading && (
          <p className="text-xs text-gray-400 text-center mt-2">{t.selectAgeAndPhoto}</p>
        )}
      </div>
    </div>
  )
}
