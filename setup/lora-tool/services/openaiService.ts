
import { fileToDataUrl } from '../utils/fileUtils';
import type { OpenAIModel } from '../types';

const API_URL = 'https://api.openai.com/v1/chat/completions';
const TEST_API_URL = 'https://api.openai.com/v1/models';

export async function generateCaptionForImage(
  imageFile: File,
  prompt: string,
  apiKey: string,
  model: OpenAIModel = 'gpt-4o'
): Promise<string> {
  if (!apiKey) {
    throw new Error('OpenAI API key is missing.');
  }

  try {
    const imageUrl = await fileToDataUrl(imageFile);

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: 'user',
            content: [
              { type: 'text', text: prompt },
              {
                type: 'image_url',
                image_url: { url: imageUrl },
              },
            ],
          },
        ],
        max_tokens: 300,
      }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        console.error('OpenAI API Error Response:', errorData);
        const errorMessage = errorData.error?.message || `HTTP error! status: ${response.status}`;
        if (response.status === 401) {
             throw new Error('OpenAI API Error: Authentication failed. Please check your API key.');
        }
        throw new Error(`OpenAI API Error: ${errorMessage}`);
    }

    const data = await response.json();
    const caption = data.choices[0]?.message?.content;

    if (caption) {
      return caption.trim();
    } else {
      throw new Error('Failed to generate caption, the response was empty.');
    }
  } catch (error) {
    console.error('Error calling OpenAI API:', error);
    throw error;
  }
}

export async function testOpenAIApiKey(apiKey: string): Promise<{ success: boolean; message: string }> {
    if (!apiKey) {
        return { success: false, message: 'API key is empty.' };
    }
    try {
        const response = await fetch(TEST_API_URL, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
            },
        });
        if (response.ok) {
            return { success: true, message: 'API key is valid!' };
        } else {
            const errorData = await response.json();
            const errorMessage = errorData.error?.message || `HTTP error! status: ${response.status}`;
             return { success: false, message: `Validation failed: ${errorMessage}` };
        }
    } catch (error) {
        return { success: false, message: `Network error during validation: ${(error as Error).message}` };
    }
}
