
import type { Settings, Checkpoint } from "../types";

const CAPTION_LENGTH_WORDS: Record<string, number> = {
  short: 12,
  medium: 28,
  long: 55,
};

function shuffle<T>(items: T[]): T[] {
  const arr = [...items];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function normalizeText(text: string): string {
  return text
    .replace(/\s+/g, ' ')
    .replace(/\s*,\s*/g, ', ')
    .replace(/,+/g, ',')
    .replace(/\s*\.\s*/g, '. ')
    .replace(/\.{2,}/g, '.')
    .replace(/ ,/g, ',')
    .trim()
    .replace(/^,|,$/g, '')
    .trim();
}

function stripBackgroundPhrases(text: string): string {
  return text
    .replace(/\b(background|backdrop|scene|scenery|environment|setting)\b[^,\.]*/gi, '')
    .replace(/\b(in the background|in the distance|behind them)\b[^,\.]*/gi, '')
    .trim();
}

function ensureTrigger(text: string, trigger: string, placeAtFront: boolean, tagStyle = false): string {
  if (!trigger) return text;
  const escaped = trigger.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');

  if (tagStyle) {
    const tokens = text.split(',').map(t => t.trim()).filter(Boolean);
    const filtered = tokens.filter(t => !new RegExp(escaped, 'i').test(t));
    const deduped = filtered.join(', ');
    return [trigger, deduped].filter(Boolean).join(', ');
  }

  const stripped = text.replace(new RegExp(`\\b${escaped}\\b`, 'gi'), '').replace(/\s+/g, ' ').trim();
  if (!new RegExp(`\\b${escaped}\\b`, 'i').test(stripped)) {
    return `${stripped}${stripped.endsWith('.') ? '' : '.'} Featuring ${trigger}.`;
  }
  return stripped;
}

function applyLengthControl(text: string, target: number, isTagStyle: boolean): string {
  if (!target) return text;
  if (isTagStyle) {
    const tokens = text.split(',').map(t => t.trim()).filter(Boolean);
    if (tokens.length <= target) return tokens.join(', ');
    return tokens.slice(0, target).join(', ');
  }
  const words = text.split(/\s+/);
  if (words.length <= target + 4) return text;
  return words.slice(0, target).join(' ').replace(/[.,;:!?]*$/, '.');
}

export function buildFinalCaption(rawDescription: string, settings: Settings, checkpoint?: Checkpoint): string {
  const { lora, captionControl, promptTopics = [] } = settings;
  const keyword = lora?.keyword?.trim() || '';
  const subjectToken = captionControl?.subjectToken?.trim() || '';

  // Model-specific formatting flags
  const model = (checkpoint || settings?.lora?.targetBaseModel || 'SDXL') as Checkpoint;
  const baseRaw = normalizeText((rawDescription || '').trim());
  const isSD = model === 'SDXL' || model === 'SD-1.5';
  const isFlux = model === 'Flux' || model === 'Chroma';
  const isWAN = model === 'WAN-2.2';
  const isQwen = model === 'Qwen-Image' || model === 'Qwen-Image-Edit';
  const trigger = [keyword, subjectToken].filter(Boolean).join(' ').trim();
  const targetWords = CAPTION_LENGTH_WORDS[captionControl?.captionLength || 'medium'];
  const cleanedRaw = captionControl?.strictFocus ? normalizeText(stripBackgroundPhrases(baseRaw)) : baseRaw;

  // Topic handling with optional shuffling and dedupe
  const topics = promptTopics
    .map(t => t?.trim())
    .filter(Boolean) as string[];
  const uniqueTopics = Array.from(new Set(topics.map(t => t.toLowerCase()))).map(
    lower => topics.find(t => t.toLowerCase() === lower) as string
  );
  const orderedTopics = captionControl?.shuffleTopics ? shuffle(uniqueTopics) : uniqueTopics;

  // Quality tags
  const qualityTags = captionControl?.addQualityTags ? ['best quality', 'high resolution'] : [];

  // For non-SD families, prefer natural language output
  if (isFlux || isWAN || isQwen) {
    let text = cleanedRaw;

    // Avoid synthetic tokens for Qwen
    if (isQwen) {
        text = text.replace(/<[^>]+>/g, '').replace(/\s{2,}/g, ' ').trim();
    }

    // Ensure trigger is present but integrated naturally (Flux/Chroma)
    text = ensureTrigger(text, trigger, false);

    // Append a short tail of topics/quality if helpful
    const tail = [...orderedTopics, ...qualityTags].join(', ');
    if (tail) {
      text = `${text} ${text.endsWith('.') ? '' : '.'} Include: ${tail}.`;
    }

    text = applyLengthControl(text, targetWords, false);
    return normalizeText(text);
  }

  // SD-style, tag oriented captions
  let parts: string[] = [];

  if (trigger) {
    parts.push(trigger);
  }

  const description = captionControl?.strictFocus ? stripBackgroundPhrases(cleanedRaw) : cleanedRaw;
  if (description) {
    parts.push(description);
  }
  
  parts.push(...orderedTopics);
  parts.push(...qualityTags);

  let finalCaption = parts.filter(Boolean).join(', ');
  finalCaption = ensureTrigger(finalCaption, trigger, true, true);
  finalCaption = applyLengthControl(finalCaption, targetWords || 40, true);
  return normalizeText(finalCaption);
}
