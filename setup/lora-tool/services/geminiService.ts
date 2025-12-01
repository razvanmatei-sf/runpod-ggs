
import { GoogleGenAI } from "@google/genai";
import { fileToBase64Part } from "../utils/fileUtils";
import { getCookie } from "../utils/cookieUtils";

export async function generateCaptionForImage(
    imageFile: File, 
    prompt: string,
): Promise<string> {
    
    try {
        const apiKey =
      getCookie('GEMINI_API_KEY')
      || (typeof localStorage !== 'undefined' && localStorage.getItem('GEMINI_API_KEY'))
      || (typeof window !== 'undefined' && (window as any).GEMINI_API_KEY)
      || (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_GEMINI_API_KEY);

    if (!apiKey) {
      throw new Error('Missing Gemini API key. Add it in the dashboard (Captioning Backend section) to continue.');
    }
    const ai = new GoogleGenAI({ apiKey });
        
        const base64Data = await fileToBase64Part(imageFile);
        const imagePart = {
            inlineData: {
                mimeType: imageFile.type,
                data: base64Data,
            },
        };
        const textPart = {
            text: prompt,
        };

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: { parts: [imagePart, textPart] }
        });

        const text = response.text;
        if (text) {
            return text.trim();
        } else {
            const safetyFeedback = response.candidates?.[0]?.safetyRatings;
            if (safetyFeedback) {
                const blocked = safetyFeedback.some(rating => rating.blocked);
                if (blocked) {
                    throw new Error("Caption generation was blocked for safety reasons. Please try a different image.");
                }
            }
            throw new Error("Failed to generate caption, the response was empty.");
        }
    } catch (error) {
        console.error("Error calling Gemini API:", error);
        
        const errorMessage = (error as Error).message;
        if (errorMessage.includes('API_KEY_INVALID') || errorMessage.includes('API key expired')) {
             throw new Error('Gemini API Error: The API key is invalid or has expired. Please check your configuration.');
        }
        if (errorMessage.includes('entity was not found')) {
            throw new Error('Gemini API Error: Requested entity not found. Please select your API key again.');
        }

        throw new Error(`Gemini API Error: ${errorMessage}`);
    }
}
