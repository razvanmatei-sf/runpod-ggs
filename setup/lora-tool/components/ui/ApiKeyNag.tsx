import React from 'react';
import type { Backend } from '../../types';

interface ApiKeyNagProps {
  onKeySelected: () => void;
  backend: Backend;
}

export const ApiKeyNag: React.FC<ApiKeyNagProps> = ({ onKeySelected, backend }) => {
  const handleSelectKey = async () => {
    if (window.aistudio && typeof window.aistudio.openSelectKey === 'function') {
      await window.aistudio.openSelectKey();
      onKeySelected();
    } else {
      console.error('aistudio.openSelectKey is not available.');
      alert('This feature requires a supported environment to select an API key automatically.');
    }
  };

  if (backend === 'gemini') {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4" aria-modal="true" role="dialog">
            <div className="w-full max-w-md rounded-2xl p-8 space-y-4 text-center text-text-secondary bg-[#11222b] shadow-2xl shadow-black/50">
                <h2 className="text-xl font-bold text-text-primary">API Key Required for Gemini</h2>
                <p className="text-sm">To generate captions, this application requires access to the Gemini API.</p>
                <div className="text-left text-sm text-text-secondary space-y-3 p-4 rounded-lg bg-black/20 border border-white/10">
                    <p>Please use the button below to select your Google Cloud project and enable the Gemini API.</p>
                </div>
                <p className="text-xs !mt-6">
                    Standard API usage fees apply. For more information, see the{' '}
                    <a href="https://ai.google.dev/gemini-api/docs/billing" target="_blank" rel="noopener noreferrer" className="font-semibold text-accent-cyan hover:underline">
                        billing documentation
                    </a>.
                </p>
                <button
                    onClick={handleSelectKey}
                    className="w-full mt-2 inline-flex items-center justify-center rounded-lg bg-gradient-to-r from-accent-cyan to-accent-violet px-6 py-3 text-sm font-semibold text-white shadow-xl shadow-violet-500/25 hover:opacity-90"
                >
                    Select Project
                </button>
            </div>
        </div>
      );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4" aria-modal="true" role="dialog">
      <div className="w-full max-w-md rounded-2xl p-8 space-y-5 bg-gradient-to-b from-[#182a34] to-[#111e28] shadow-2xl shadow-black/50">
        <h2 className="text-xl font-bold text-center text-text-primary">API Key Required for Gemini</h2>
        <p className="text-sm text-center text-text-secondary">
          To generate captions, this application requires access to the Gemini API.
        </p>
        <div className="text-sm space-y-3 p-4 rounded-lg border border-white/10 text-text-secondary">
          <p>
              Please enter your Gemini API key in the <strong className="font-semibold text-text-primary">"Captioning Backend"</strong> section of the Configuration panel.
          </p>
          <hr className="border-white/10 my-3" />
          <p className="text-xs">
              Your key is saved securely in your browser's local storage and is not transmitted anywhere except to Gemini's servers.
          </p>
        </div>
        <p className="text-xs text-center !mt-6 text-text-secondary">
          Standard API usage fees apply. For more information, see the{' '}
          <a
            href="https://ai.google.dev/pricing"
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-accent-cyan hover:underline"
          >
            billing documentation
          </a>.
        </p>
      </div>
    </div>
  );
};
