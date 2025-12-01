
import React, { useCallback, useState, useMemo, useRef, useEffect } from 'react';
import type { TrainingImage } from '../types';
import { UploadIcon, SpinnerIcon, CheckCircleIcon, XCircleIcon } from './Icons';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { preprocessImageFile } from '../utils/fileUtils';

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
};

const ImageCard: React.FC<{ image: TrainingImage }> = ({ image }) => {
    const progress = image.progress || 0;
    return (
        <motion.div 
          layout
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
          className="relative aspect-square rounded-lg overflow-hidden bg-slate-800/50 group"
        >
            <img src={image.previewUrl} alt={image.file.name} className="w-full h-full object-cover" />
            
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="p-2 text-xs text-slate-200 text-center break-words">{image.caption || (image.status === 'error' ? 'Error' : 'Awaiting caption...')}</div>
            </div>

            <div className="absolute top-2 right-2 z-10">
                {image.status === 'done' && <div className="text-green-400"><CheckCircleIcon /></div>}
                {image.status === 'error' && <div className="text-red-400"><XCircleIcon /></div>}
            </div>

            {image.status === 'processing' && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <svg className="w-16 h-16" viewBox="0 0 100 100">
                        <circle className="text-slate-700" strokeWidth="5" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50" />
                        <motion.circle
                            className="text-cyan-400"
                            strokeWidth="5"
                            strokeLinecap="round"
                            stroke="currentColor"
                            fill="transparent"
                            r="40"
                            cx="50"
                            cy="50"
                            style={{ pathLength: progress / 100, rotate: -90 }}
                        />
                    </svg>
                </div>
            )}
        </motion.div>
    );
};

interface ImageWorkspaceProps {
  images: TrainingImage[];
  setImages: React.Dispatch<React.SetStateAction<TrainingImage[]>>;
  onProcess: () => void;
  onDownload: () => void;
  isProcessing: boolean;
  log: (message: string) => void;
}

export const ImageWorkspace: React.FC<ImageWorkspaceProps> = ({ images, setImages, onProcess, onDownload, isProcessing, log }) => {
  const [isDragging, setIsDragging] = useState(false);
  const objectUrlsRef = useRef<string[]>([]);
  const MAX_IMAGE_DIMENSION = 2048;

  useEffect(() => {
    return () => {
      objectUrlsRef.current.forEach(url => URL.revokeObjectURL(url));
    };
  }, []);
  
  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files) return;
    const accepted = Array.from(files).filter(file => file.type.startsWith('image/'));
    const processed = await Promise.all(accepted.map(async (file) => {
      const safeFile = await preprocessImageFile(file, MAX_IMAGE_DIMENSION);
      const previewUrl = URL.createObjectURL(safeFile);
      objectUrlsRef.current.push(previewUrl);
      return {
        id: `${safeFile.name}-${safeFile.lastModified}`,
        file: safeFile,
        previewUrl,
        status: 'pending' as const,
        progress: 0,
      };
    }));

    setImages(prev => {
      const existingIds = new Set(prev.map(p => p.id));
      const uniqueNew = processed.filter(n => !existingIds.has(n.id));
      log(`Loaded ${uniqueNew.length} new images (preprocessed to strip metadata/downscale if needed).`);
      return [...prev, ...uniqueNew];
    });
  }, [setImages, log]);

  const handleDrop = useCallback((event: React.DragEvent<HTMLLabelElement>) => {
      event.preventDefault();
      event.stopPropagation();
      setIsDragging(false);
      void handleFiles(event.dataTransfer.files);
  }, [handleFiles]);

  const handleDragEnter = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    event.stopPropagation();
    if(event.dataTransfer.items && event.dataTransfer.items.length > 0){
        setIsDragging(true);
    }
  };
  const handleDragLeave = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };
  
  const allDone = useMemo(() => images.length > 0 && images.every(img => img.status === 'done' || img.status === 'error'), [images]);

  return (
    <div className="panel p-6 space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
            <h2 className="text-xl font-bold">Workspace</h2>
            <p className="text-sm text-text-secondary">{images.length} images loaded</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={onProcess} 
            disabled={isProcessing || images.length === 0 || allDone} 
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-accent-cyan to-accent-violet px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
          >
              {isProcessing ? <><SpinnerIcon /> <span>Processing...</span></> : <><span>Process Images</span></>}
          </button>
          <button 
            onClick={onDownload} 
            disabled={isProcessing || !allDone} 
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
             Download ZIP
          </button>
        </div>
      </div>
      
      <div className="rounded-lg bg-black/20 p-4 transition-all duration-300">
        {images.length === 0 ? (
          <label 
            onDrop={handleDrop}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragEnter}
            className={clsx(
                "relative flex flex-col items-center justify-center w-full h-56 rounded-lg border-2 border-dashed border-slate-700 p-12 text-center hover:border-slate-500 cursor-pointer transition-all duration-300",
                isDragging && "border-violet-500 bg-violet-500/10 scale-105"
            )}>
            <UploadIcon/>
            <span className="mt-2 block text-sm font-semibold text-slate-300">
              Drop images here, or click to select files
            </span>
             <input type="file" multiple accept="image/*" onChange={e => void handleFiles(e.target.files)} className="sr-only" />
          </label>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            <AnimatePresence>
                {images.map(image => <ImageCard key={image.id} image={image} />)}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};
