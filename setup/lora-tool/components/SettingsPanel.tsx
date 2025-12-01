
import React, { useEffect, useState } from 'react';
import type { Settings, Checkpoint, UseCase } from '../types';
import { getConfig } from '../services/configService';
import { InfoIcon } from './Icons';
import { motion } from 'framer-motion';
import { getCookie, setCookie } from '../utils/cookieUtils';

interface SettingsPanelProps {
  settings: Settings;
  onSettingsChange: (newOverrides: Partial<Settings>) => void;
  onSelectionChange: (checkpoint: Checkpoint, useCase: UseCase) => void;
  selectedCheckpoint: Checkpoint;
  selectedUseCase: UseCase;
  log: (message: string) => void;
}

const config = getConfig();
const { checkpoint_order, use_case_order } = config.ui_hints;

const tooltips: Record<string, string> = {
    backend: "Choose your preferred AI provider for generating captions.",
    trainingGoal: "Select the primary objective for your LoRA. This choice automatically applies best-practice settings for guidance, strength, and other controls.",
    filePrefix: "A consistent name used for all your image and text files (e.g., 'audrey_0001.jpg').",
    keyword: "The main trigger word to identify your subject. Use a unique, single word if possible.",
    targetBaseModel: "Choose the base model you intend to use your LoRA with. Settings will be optimized for this choice.",
    captionGuidance: "Instruct the AI on the desired style and content of the captions. Be descriptive. This is the most impactful setting.",
    guidanceStrength: "Controls how strongly the AI adheres to your Caption Guidance. Higher values mean stricter adherence.",
    negativeHints: "Tell the AI what to specifically AVOID describing in the captions (e.g., objects, colors, or styles).",
    captionLength: "Sets the target length for the generated captions. 'Short' is often better for identity, 'Long' for style or cinematic LoRAs.",
    negativePreset: "Automatically adds common negative prompts depending on the base model to improve quality.",
    strictFocus: "Forces the AI to only describe the main subject, ignoring background and other elements. Ideal for character LoRAs.",
    addQualityTags: "Appends common quality-enhancing tags like 'best quality', 'high resolution' to your captions.",
    shuffleTopics: "Randomizes the order of Prompt Topics for each image, which can help prevent the model from associating topics with each other.",
    subjectToken: "An additional token (e.g., <sks>) that can be used with your keyword for more stable subject identity.",
    promptTopics: "Specific keywords or phrases that will be added to every caption to reinforce certain concepts like a style, an object, or a consistent color.",
    processingDelay: "The delay in seconds between processing each image. Increasing this can help avoid API rate-limiting errors."
};

const Tooltip: React.FC<{ text: string }> = ({ text }) => (
    <div className="relative group flex items-center">
        <InfoIcon />
        <div className="absolute left-full bottom-0 ml-2 w-64 p-3 bg-slate-900 border border-border-color rounded-lg text-xs text-text-secondary opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
            {text}
        </div>
    </div>
);


const Section: React.FC<{title: string, children: React.ReactNode}> = ({ title, children }) => (
    <details className="space-y-4" open>
        <summary className="cursor-pointer text-sm font-bold uppercase tracking-wider text-cyan-400 list-none flex items-center gap-2">
            {title}
        </summary>
        <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="pt-4 space-y-4 border-t border-white/10 overflow-hidden"
        >
            {children}
        </motion.div>
    </details>
);

const Field: React.FC<{label: string, tooltipKey?: string, children: React.ReactNode}> = ({ label, tooltipKey, children }) => (
    <div>
        <div className="flex items-center gap-2 mb-1.5">
            <label className="block text-sm font-medium text-text-secondary">{label}</label>
            {tooltipKey && tooltips[tooltipKey] && <Tooltip text={tooltips[tooltipKey]} />}
        </div>
        {children}
    </div>
);

export const SettingsPanel: React.FC<SettingsPanelProps> = ({ 
    settings,
    onSettingsChange, 
    onSelectionChange, 
    selectedCheckpoint, 
    selectedUseCase,
}) => {
  const [apiKey, setApiKey] = useState('');
  const [apiKeySaved, setApiKeySaved] = useState(false);

  useEffect(() => {
    const saved = getCookie('GEMINI_API_KEY');
    if (saved) {
      setApiKey(saved);
      setApiKeySaved(true);
    }
  }, []);

  const handleLoraChange = (field: keyof Settings['lora'], value: any) => {
    onSettingsChange({ lora: { ...settings.lora, [field]: value } });
  }
  const handleCaptionControlChange = (field: keyof Settings['captionControl'], value: any) => {
    onSettingsChange({ captionControl: { ...settings.captionControl, [field]: value } });
  }
  const handlePromptTopicChange = (index: number, value: string) => {
      const newTopics = [...(settings.promptTopics || [])];
      newTopics[index] = value;
      onSettingsChange({ promptTopics: newTopics });
  }

  return (
    <div className="panel p-6 h-full">
      <h2 className="text-xl font-bold mb-6">Configuration</h2>
      <div className="space-y-8 max-h-[calc(100vh-10rem)] overflow-y-auto pr-2 -mr-2">
        
        <Section title="Captioning Backend">
            <Field label="Service">
                <input type="text" readOnly disabled className="form-input bg-slate-800/50 cursor-not-allowed" value="Google Gemini" />
            </Field>
            <Field label="Gemini API Key">
                <div className="flex gap-2">
                    <input
                      type="password"
                      className="form-input flex-1"
                      placeholder="Paste your Gemini API key"
                      value={apiKey}
                      onChange={e => {
                        setApiKey(e.target.value.trim());
                        setApiKeySaved(false);
                      }}
                    />
                    <button
                      type="button"
                      className="rounded-md bg-slate-700 px-3 text-sm font-semibold text-white hover:bg-slate-600 transition-colors"
                      onClick={() => {
                        setCookie('GEMINI_API_KEY', apiKey, 365);
                        setApiKeySaved(true);
                      }}
                      disabled={!apiKey}
                    >
                      Save
                    </button>
                </div>
                <p className="text-xs text-text-secondary mt-1">
                  Stored in a cookie for this browser only. Not sent anywhere except Gemini when generating captions.
                  {apiKeySaved && <span className="text-green-400 ml-1">Saved.</span>}
                </p>
            </Field>
            <p className="text-xs text-text-secondary">No .env required—enter your key here to start captioning.</p>
        </Section>
        
        <Section title="LORA Settings">
            <Field label="Training Goal" tooltipKey="trainingGoal">
                 <select value={selectedUseCase} onChange={e => onSelectionChange(selectedCheckpoint, e.target.value as UseCase)} className="form-select">
                    {use_case_order.map(uc => <option key={uc} value={uc}>{uc.charAt(0).toUpperCase() + uc.slice(1)}</option>)}
                </select>
            </Field>
            <div className="grid grid-cols-2 gap-4">
                <Field label="File prefix" tooltipKey="filePrefix">
                    <input type="text" className="form-input" value={settings.lora?.filePrefix || ''} onChange={e => handleLoraChange('filePrefix', e.target.value)} />
                </Field>
                <Field label="Keyword" tooltipKey="keyword">
                    <input type="text" className="form-input" value={settings.lora?.keyword || ''} onChange={e => handleLoraChange('keyword', e.target.value)} />
                </Field>
            </div>
            <Field label="Target Base Model" tooltipKey="targetBaseModel">
                <select value={selectedCheckpoint} onChange={e => onSelectionChange(e.target.value as Checkpoint, selectedUseCase)} className="form-select">
                    {checkpoint_order.map(cp => <option key={cp} value={cp}>{cp}</option>)}
                </select>
            </Field>
        </Section>
        
        <Section title="Caption Control">
            <Field label="Caption Guidance" tooltipKey="captionGuidance">
                <textarea rows={4} className="form-textarea" value={settings.captionControl?.guidance || ''} onChange={e => handleCaptionControlChange('guidance', e.target.value)} />
            </Field>
             <Field label={`Guidance Strength: ${settings.captionControl?.guidanceStrength || 0.7}`} tooltipKey="guidanceStrength">
                <input type="range" min="0" max="1" step="0.1" value={settings.captionControl?.guidanceStrength || 0.7} onChange={e => handleCaptionControlChange('guidanceStrength', parseFloat(e.target.value))} />
            </Field>
            <Field label="Negative Hints" tooltipKey="negativeHints">
                <input type="text" className="form-input" value={settings.captionControl?.negativeHints || ''} onChange={e => handleCaptionControlChange('negativeHints', e.target.value)} />
            </Field>
            <div className="grid grid-cols-2 gap-4">
                <Field label="Caption Length" tooltipKey="captionLength">
                    <select className="form-select" value={settings.captionControl?.captionLength || 'medium'} onChange={e => handleCaptionControlChange('captionLength', e.target.value)}>
                        <option value="short">Short</option>
                        <option value="medium">Medium</option>
                        <option value="long">Long</option>
                    </select>
                </Field>
                <Field label="Negative Preset" tooltipKey="negativePreset">
                    <select className="form-select" value={settings.captionControl?.negativePreset || 'custom_merge'} onChange={e => handleCaptionControlChange('negativePreset', e.target.value)}>
                        <option value="auto">Auto</option>
                        <option value="custom_merge">Custom Merge</option>
                        <option value="none">None</option>
                    </select>
                </Field>
            </div>
            <div className="space-y-2 text-sm">
                <label className="flex items-center gap-3">
                    <input type="checkbox" className="form-checkbox" checked={settings.captionControl?.strictFocus} onChange={e => handleCaptionControlChange('strictFocus', e.target.checked)} />
                    <span className="flex items-center gap-2">Strict focus (subject-only) <Tooltip text={tooltips.strictFocus} /></span>
                </label>
                 <label className="flex items-center gap-3">
                    <input type="checkbox" className="form-checkbox" checked={settings.captionControl?.addQualityTags} onChange={e => handleCaptionControlChange('addQualityTags', e.target.checked)} />
                    <span className="flex items-center gap-2">Add quality tags <Tooltip text={tooltips.addQualityTags} /></span>
                </label>
                 <label className="flex items-center gap-3">
                    <input type="checkbox" className="form-checkbox" checked={settings.captionControl?.shuffleTopics} onChange={e => handleCaptionControlChange('shuffleTopics', e.target.checked)} />
                    <span className="flex items-center gap-2">Shuffle topics per image <Tooltip text={tooltips.shuffleTopics} /></span>
                </label>
            </div>
             <Field label="Subject Token" tooltipKey="subjectToken">
                <input type="text" className="form-input" value={settings.captionControl?.subjectToken || ''} onChange={e => handleCaptionControlChange('subjectToken', e.target.value)} />
            </Field>
            <Field label="Processing Delay (seconds)" tooltipKey="processingDelay">
                <input type="number" min="0" step="0.1" className="form-input" value={settings.captionControl?.processingDelay || 1} onChange={e => handleCaptionControlChange('processingDelay', parseFloat(e.target.value))} />
            </Field>
        </Section>
        
        <Section title="Prompt Topics">
             <div className="flex items-center gap-2 mb-1.5">
                <p className="text-sm font-medium text-text-secondary">Topics to reinforce in every caption</p>
                <Tooltip text={tooltips.promptTopics} />
            </div>
            <div className="grid grid-cols-2 gap-3">
                {[...Array(6)].map((_, i) => (
                    <div key={i}>
                        <input type="text" className="form-input" placeholder={`Topic ${i + 1}`} value={settings.promptTopics?.[i] || ''} onChange={e => handlePromptTopicChange(i, e.target.value)} />
                    </div>
                ))}
            </div>
        </Section>

      </div>
    </div>
  );
};
