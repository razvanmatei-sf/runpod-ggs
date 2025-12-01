
export function fileToBase64Part(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      // remove the data url prefix, e.g. "data:image/jpeg;base64,"
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
}

export function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      resolve(reader.result as string);
    };
    reader.onerror = (error) => reject(error);
  });
}

function loadImageFromUrl(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
}

/**
 * Re-encodes the image via canvas to strip EXIF metadata and optionally downscale.
 * Falls back to the original file if processing fails.
 */
export async function preprocessImageFile(file: File, maxDimension = 2048): Promise<File> {
  try {
    const dataUrl = await fileToDataUrl(file);
    const img = await loadImageFromUrl(dataUrl);

    const scale = Math.min(1, maxDimension / Math.max(img.width, img.height));
    const width = Math.max(1, Math.round(img.width * scale));
    const height = Math.max(1, Math.round(img.height * scale));

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Could not get 2D context for preprocessing.');
    ctx.drawImage(img, 0, 0, width, height);

    const mimeType = file.type || 'image/jpeg';
    const blob: Blob = await new Promise((resolve, reject) => {
      canvas.toBlob(b => (b ? resolve(b) : reject(new Error('Failed to encode image.'))), mimeType, 0.95);
    });

    return new File([blob], file.name, { type: mimeType, lastModified: Date.now() });
  } catch (err) {
    console.warn('Preprocessing image failed, using original file.', err);
    return file;
  }
}
