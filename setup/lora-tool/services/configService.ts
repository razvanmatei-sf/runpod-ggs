
import type { Config, Settings, Checkpoint, UseCase } from '../types';

function mergeDeep<T extends object>(target: T, ...sources: Partial<T>[]): T {
    if (!sources.length) return target;
    const source = sources.shift();
    if (source === undefined) return target;

    for (const key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
            const sourceKey = key as keyof T;
            if (source[sourceKey] && typeof source[sourceKey] === 'object' && !Array.isArray(source[sourceKey])) {
                if (!target[sourceKey] || typeof target[sourceKey] !== 'object') {
                    Object.assign(target, { [key]: {} });
                }
                mergeDeep(target[sourceKey] as object, source[sourceKey] as object);
            } else {
                Object.assign(target, { [key]: source[sourceKey] });
            }
        }
    }

    return mergeDeep(target, ...sources);
}

const configData: Config = {
  "version": "1.5.0",
  "ui_hints": {
    "checkpoint_order": ["SDXL", "Flux", "Qwen-Image", "WAN-2.2", "SD-1.5", "Chroma", "Qwen-Image-Edit", "custom"],
    "use_case_order": ["identity", "likeness", "cinematic", "clothing", "pose", "abstract"]
  },
  "inheritance": {
    "order": ["global_defaults", "checkpoint_overrides", "use_case"],
    "allow_unknown_keys": true
  },
  "global_defaults": {
    "lora": { "filePrefix": "lora_img", "keyword": "my_subject" },
    "captionControl": {
        "guidance": "A detailed, high-quality description of the subject, its features, and the surrounding environment.",
        "guidanceStrength": 0.7,
        "negativeHints": "blurry, low quality, watermark, signature, text",
        "captionLength": "medium",
        "negativePreset": "auto",
        "strictFocus": false,
        "addQualityTags": true,
        "shuffleTopics": false,
        "subjectToken": "<subject>",
        "processingDelay": 1
    },
    "promptTopics": ["photorealistic", "sharp focus", "4k", "", "", ""],
  },
  "checkpoints": {
    "SDXL": {
      "notes": "Favors natural-language captions. Best for high detail.",
      "overrides": { "captionControl": { "addQualityTags": true } },
      "use_cases": {
        "identity": {
            "captionControl": { "guidance": "A photorealistic portrait of a specific person, focusing on consistent facial identity, sharp features, and neutral lighting. Capture the essence of the person for strong likeness.", "strictFocus": true, "guidanceStrength": 0.8 },
            "promptTopics": ["photorealistic", "skin texture", "sharp focus", "detailed eyes", "neutral background", ""]
        },
        "cinematic": {
            "captionControl": { "guidance": "A cinematic movie still. Describe the mood, lighting (e.g., tungsten, neon), lens effects (e.g., bokeh, lens flare), and overall atmosphere. Mention film stock and composition.", "strictFocus": false, "negativeHints": "boring, flat lighting, amateur photo" },
            "promptTopics": ["cinematic", "film grain", "moody lighting", "anamorphic", "high contrast", ""]
        },
        "clothing": {
            "captionControl": { "guidance": "A studio fashion shot focusing on the details of the garment. Describe the material (e.g., silk, denim), cut, fit, and any patterns or accessories.", "strictFocus": true, "negativeHints": "wrinkled fabric, poor fit" },
            "promptTopics": ["fashion photography", "studio lighting", "detailed fabric", "clean background", "", ""]
        },
        "pose": {
            "captionControl": { "guidance": "A full-body shot of a person, clearly capturing their pose. Describe the pose, angle, and framing for accurate representation.", "strictFocus": true },
            "promptTopics": ["full body shot", "dynamic pose", "clear silhouette", "plain background", "", ""]
        },
        "abstract": {
            "captionControl": { "guidance": "An abstract image focusing on effects, colors, and textures. Describe the visual elements like light, color process, and medium used.", "strictFocus": false },
            "promptTopics": ["abstract art", "halation", "film grain", "duotone", "experimental", ""]
        }
      }
    },
    "Flux": { 
      "notes": "Prefers shorter, natural language captions.",
      "overrides": { "captionControl": { "captionLength": "short", "guidanceStrength": 0.6 } },
      "use_cases": { "identity": { "captionControl": { "guidance": "A clear photo of a person. Focus on their main facial features and hair style.", "strictFocus": true }, "promptTopics": ["natural photo", "clear face", "soft lighting", "", "", ""] }, "cinematic": { "captionControl": { "guidance": "A cinematic photo. Describe the overall mood and lighting.", "strictFocus": false }, "promptTopics": ["cinematic", "natural lighting", "emotional mood", "", "", ""] } }
    },
    "Qwen-Image": {
      "notes": "Natural-language captions; short often works for likeness.",
      "overrides": { "captionControl": { "addQualityTags": true, "negativeHints": "watermark, jpeg artifacts, low quality" } },
      "use_cases": { "identity": { "captionControl": { "guidance": "[trigger], portrait, neutral background, capturing clear facial features.", "captionLength": "short", "strictFocus": true }, "promptTopics": ["Ultra HD", "4K", "sharp focus", "neutral background", "", ""] }, "cinematic": { "captionControl": { "guidance": "A cinematic scene with moody lighting and a strong sense of atmosphere. Describe the scene's emotional tone.", "captionLength": "medium" }, "promptTopics": ["cinematic composition", "Ultra HD", "moody", "", "", ""] } }
    },
    "WAN-2.2": {
      "notes": "Video LoRA: captions should describe actions and movement.",
      "overrides": { "captionControl": { "negativeHints": "watermark, blown highlights, motion blur", "guidanceStrength": 0.8 } },
      "use_cases": { "identity": { "captionControl": { "guidance": "A video frame of a person. Describe their action, expression, and the shot type (e.g., medium shot, close-up).", "captionLength": "medium" }, "promptTopics": ["video frame", "4k", "consistent action", "clear motion", "", ""] }, "cinematic": { "captionControl": { "guidance": "A cinematic video frame. Describe the camera movement (e.g., dolly-in, slow pan), lighting, and overall mood.", "captionLength": "medium" }, "promptTopics": ["cinematic", "film look", "camera movement", "high contrast", "", ""] } }
    },
    "SD-1.5": { 
      "notes": "Works best with tag-style captions and simple descriptions.",
      "overrides": { "captionControl": { "addQualityTags": false, "negativePreset": "custom_merge", "negativeHints": "extra fingers, deformed, ugly, bad anatomy" } },
      "use_cases": { "identity": { "captionControl": { "guidance": "portrait photo of a person, detailed face, clear features, (style)", "strictFocus": true, "captionLength": "short" }, "promptTopics": ["detailed face", "sharp eyes", "soft lighting", "", "", ""] }, "clothing": { "captionControl": { "guidance": "photo of a person wearing a [color] [garment], full body shot, studio setting", "strictFocus": false, "captionLength": "short" }, "promptTopics": ["full body", "studio photography", "plain background", "", "", ""] }, "pose": { "captionControl": { "guidance": "A full body photo of a person doing a [pose name] pose, clear view of limbs", "strictFocus": true, "captionLength": "short" }, "promptTopics": ["full body shot", "dynamic pose", "action shot", "", "", ""] } }
    },
    "Chroma": { "notes": "Flux-based; inherits Flux rules unless overridden.", "use_cases": {} },
    "Qwen-Image-Edit": { "notes": "Supports paired control images.", "use_cases": {} },
    "custom": { "notes": "A blank slate. Start from global defaults and customize.", "use_cases": {} }
  }
};

export function getEffectiveConfig(checkpoint: Checkpoint, useCase: UseCase): Settings {
    const checkpointConfig = configData.checkpoints[checkpoint];
    if (!checkpointConfig) {
        return JSON.parse(JSON.stringify(configData.global_defaults));
    }

    const globalDefaults = JSON.parse(JSON.stringify(configData.global_defaults));
    const checkpointOverrides = JSON.parse(JSON.stringify(checkpointConfig.overrides || {}));
    const useCaseSettings = JSON.parse(JSON.stringify(checkpointConfig.use_cases[useCase] || {}));
    
    return mergeDeep(globalDefaults, checkpointOverrides, useCaseSettings);
}

export const getConfig = (): Config => configData;