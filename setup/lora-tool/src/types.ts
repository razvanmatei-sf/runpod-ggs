
// FIX: Added missing Backend and OpenAIModel types used in other components.
export type Backend = "gemini" | "openai";
export type OpenAIModel = 'gpt-4o' | 'gpt-4-turbo';

export type Checkpoint = "SDXL" | "Flux" | "Chroma" | "Qwen-Image" | "Qwen-Image-Edit" | "WAN-2.2" | "SD-1.5" | "custom";
export type UseCase = "identity" | "likeness" | "cinematic" | "clothing" | "pose" | "abstract";

export interface TrainingImage {
  id: string;
  file: File;
  previewUrl: string;
  status: 'pending' | 'processing' | 'done' | 'error';
  caption?: string;
  progress?: number;
}

export interface LoraSettings {
    filePrefix: string;
    keyword: string;
    targetBaseModel: Checkpoint;
}

export interface CaptionControlSettings {
    guidance: string;
    guidanceStrength: number;
    negativeHints: string;
    captionLength: 'short' | 'medium' | 'long';
    negativePreset: 'auto' | 'custom_merge' | 'none';
    strictFocus: boolean;
    addQualityTags: boolean;
    shuffleTopics: boolean;
    subjectToken: string;
    processingDelay: number;
}

export interface Settings {
  lora?: Partial<LoraSettings>;
  captionControl?: Partial<CaptionControlSettings>;
  promptTopics?: (string | undefined)[];
  
  captioning?: {
    prompt_length?: string;
    trigger_placement?: string;
    caption_style?: string;
    prompt_template?: string;
    tokens?: {
      must_include?: string[];
      must_avoid?: string[];
    };
  };
  structuring?: {
    image_naming?: string;
    directory_pattern?: string;
    repeats_default?: number;
  };
  notes?: string;
}

export interface Config {
  version: string;
  ui_hints: {
    checkpoint_order: Checkpoint[];
    use_case_order: UseCase[];
  };
  inheritance: {
    order: string[];
    allow_unknown_keys: boolean;
  };
  global_defaults: Settings;
  checkpoints: Record<Checkpoint, {
    notes?: string;
    overrides?: Settings;
    use_cases: Partial<Record<UseCase, Settings>>;
  }>;
}
