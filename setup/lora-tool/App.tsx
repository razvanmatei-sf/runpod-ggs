

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Header } from './components/Header';
import { SettingsPanel } from './components/SettingsPanel';
import { ImageWorkspace } from './components/ImageWorkspace';
import { Console } from './components/Console';
import { generateCaptionForImage as generateGeminiCaption } from './services/geminiService';
import { buildFinalCaption } from './utils/captionUtils';
import { getEffectiveConfig } from './services/configService';
import { useRef } from 'react';
import type { TrainingImage, Settings, UseCase, Checkpoint } from './types';
import JSZip from 'jszip';

const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

export default function App() {
  const [images, setImages] = useState<TrainingImage[]>([]);
  const [selectedCheckpoint, setSelectedCheckpoint] = useState<Checkpoint>('SDXL');
  const [selectedUseCase, setSelectedUseCase] = useState<UseCase>('identity');
  const lastLogRef = useRef<string>('');

  const baseSettings = useMemo(() => getEffectiveConfig(selectedCheckpoint, selectedUseCase), [selectedCheckpoint, selectedUseCase]);
  const [userOverrides, setUserOverrides] = useState<Partial<Settings>>({});
  
  const settings: Settings = useMemo(() => {
    const merged = JSON.parse(JSON.stringify(baseSettings));
    for (const key in userOverrides) {
        if (typeof userOverrides[key as keyof Settings] === 'object' && userOverrides[key as keyof Settings] !== null && !Array.isArray(userOverrides[key as keyof Settings])) {
            merged[key as keyof Settings] = { ...(merged[key as keyof Settings] || {}), ...userOverrides[key as keyof Settings] };
        } else {
            merged[key as keyof Settings] = userOverrides[key as keyof Settings];
        }
    }
    return merged;
  }, [baseSettings, userOverrides]);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  
  const log = useCallback((message: string) => {
    const trimmed = message.trim();
    if (trimmed === lastLogRef.current) return;
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    lastLogRef.current = trimmed;
    setLogs(prevLogs => [`[${timestamp}] ${message}`, ...prevLogs]);
  }, []);

  useEffect(() => {
    log('🚦 LORA Helper initialized. Bring on the pixels!');
  }, [log]);
  
  const handleSettingsChange = useCallback((newOverrides: Partial<Settings>) => {
    setUserOverrides(prev => ({ ...prev, ...newOverrides }));
  }, []);

  const handleSelectionChange = useCallback((checkpoint: Checkpoint, useCase: UseCase) => {
    setSelectedCheckpoint(checkpoint);
    setSelectedUseCase(useCase);
    setUserOverrides({}); 
    log(`Switched context to Checkpoint: ${checkpoint}, Use Case: ${useCase}`);
  }, [log]);
  
  const constructAIPrompt = (): string => {
    const { captionControl } = settings;
    if (!captionControl) return "A photorealistic portrait of a specific person, capturing their distinct facial features, hair, and expression.";

    let promptParts = [captionControl.guidance || "A photorealistic portrait of a specific person, capturing their distinct facial features, hair, and expression."];
    
    if (captionControl.negativeHints) {
        promptParts.push(`\nAVOID describing elements like: ${captionControl.negativeHints}.`);
    }

    promptParts.push(`\nFocus on creating a caption of ${captionControl.captionLength || 'medium'} length.`);
    
    return promptParts.join(' ');
  }

  const processImages = useCallback(async () => {
    if (images.length === 0) {
      log('🤷‍♂️ Nothing to caption. Drop some images first!');
      return;
    }
    log(`🚀 Starting caption run for ${images.length} image(s) with Gemini—hold onto your GPUs.`);
    setIsProcessing(true);

    const imagesToProcess = [...images];
    setImages(imgs => imgs.map(img => (img.status === 'error' || img.status === 'pending' ? { ...img, status: 'processing', progress: 0 } : img)));
    
    const masterPrompt = constructAIPrompt();
    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < imagesToProcess.length; i++) {
      const imageToProcess = imagesToProcess[i];
      if (imageToProcess.status === 'done') continue;

      const { id, file } = imageToProcess;
      const imageName = file.name;

      try {
        log(`🖼️ Processing ${imageName} (${i + 1}/${imagesToProcess.length})...`);
        setImages(currentImages => currentImages.map(img => img.id === id ? { ...img, status: 'processing', progress: 30 } : img));

        const rawDescription = await generateGeminiCaption(file, masterPrompt);

        const finalCaption = buildFinalCaption(rawDescription, settings, selectedCheckpoint);
        
        setImages(currentImages => currentImages.map(img => 
            img.id === id 
            ? { ...img, caption: finalCaption, status: 'done', progress: 100 } 
            : img
        ));

        successCount += 1;
        log(`✅ Captioned ${imageName}. Brain cells well spent.`);
      } catch (error) {
        console.error('Error processing image:', error);
        const errorMessage = (error as Error).message;
        errorCount += 1;
        log(`💥 Gemini balked at ${imageName}: ${errorMessage}`);
        
        setImages(currentImages => currentImages.map(img => 
            img.id === id 
            ? { ...img, status: 'error', progress: 0, caption: `Error: ${errorMessage}` } 
            : img
        ));
      }
      
      if (i < imagesToProcess.length - 1) {
        const delayTime = (settings.captionControl?.processingDelay || 1) * 1000;
        await delay(delayTime);
      }
    }
    log(`🎉 Caption run finished. Wins: ${successCount}, Oopsies: ${errorCount}.`);
    setIsProcessing(false);
  }, [images, settings, log]);

  const handleDownload = useCallback(async () => {
    log('Preparing ZIP file for download...');
    const zip = new JSZip();
    const prefix = settings.lora?.filePrefix || 'image';
    
    images.forEach((image, index) => {
      if (image.status === 'done') {
        const fileExtension = image.file.name.split('.').pop()?.toLowerCase() || 'jpg';
        const newImageName = `${prefix}_${(index + 1).toString().padStart(4, '0')}.${fileExtension}`;
        const newTxtName = `${prefix}_${(index + 1).toString().padStart(4, '0')}.txt`;
        zip.file(newImageName, image.file);
        zip.file(newTxtName, image.caption || '');
      }
    });

    zip.generateAsync({ type: 'blob' }).then(content => {
      const link = document.createElement('a');
      link.href = URL.createObjectURL(content);
      link.download = `${prefix}_dataset.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      log('Download started.');
    });
  }, [images, settings.lora?.filePrefix, log]);

  return (
    <div className="min-h-screen">
      <div className="animated-glow" aria-hidden="true"></div>
      <Header />
      <main className="relative z-10 mx-auto max-w-[1920px] p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4 xl:col-span-3">
            <SettingsPanel
              settings={settings}
              onSettingsChange={handleSettingsChange}
              onSelectionChange={handleSelectionChange}
              selectedCheckpoint={selectedCheckpoint}
              selectedUseCase={selectedUseCase}
              log={log}
            />
          </div>
          <div className="lg:col-span-8 xl:col-span-9 space-y-6">
            <ImageWorkspace
              images={images}
              setImages={setImages}
              onProcess={processImages}
              onDownload={handleDownload}
              isProcessing={isProcessing}
              log={log}
            />
            <Console logs={logs} />
          </div>
        </div>
      </main>
    </div>
  );
}
