"""
Fixed HuggingFace API Interface
"""

import requests
import json
import time
from typing import Optional, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceAPI:
    """Fixed HuggingFace API Interface"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        
        # Try smaller models first
        self.model_options = [
            "microsoft/phi-2",                      # 2.7B - Fastest
            "Qwen/Qwen2.5-7B-Instruct",            # 7B - Good balance
            "mistralai/Mistral-7B-Instruct-v0.2",  # 7B - Good quality
            "Qwen/Qwen2.5-72B-Instruct"           # 72B - Only if others fail
        ]
        
        self.current_model_index = 0
        self.current_model = self.model_options[self.current_model_index]
    
    def _get_api_url(self):
        """Get API URL for current model"""
        return f"https://api-inference.huggingface.co/models/{self.current_model}"
    
    def _try_next_model(self):
        """Switch to next model if current fails"""
        if self.current_model_index < len(self.model_options) - 1:
            self.current_model_index += 1
            self.current_model = self.model_options[self.current_model_index]
            logger.info(f"Switching to model: {self.current_model}")
            return True
        return False
    
    def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        """Generate text with automatic retry and model fallback"""
        
        original_prompt = prompt[:500]  # Save for logging
        
        for model_attempt in range(len(self.model_options)):
            api_url = self._get_api_url()
            
            # Prepare payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": min(max_tokens, 1024),  # Limit tokens
                    "temperature": temperature,
                    "top_p": 0.95,
                    "do_sample": True,
                    "return_full_text": False
                },
                "options": {
                    "use_cache": True,
                    "wait_for_model": True  # Wait if model is loading
                }
            }
            
            for retry in range(3):  # Retry 3 times per model
                try:
                    logger.info(f"Calling model: {self.current_model} (Attempt {retry + 1})")
                    
                    response = requests.post(
                        api_url,
                        headers=self.headers,
                        json=payload,
                        timeout=45  # Increased timeout
                    )
                    
                    logger.info(f"Response status: {response.status_code}")
                    
                    # Handle different status codes
                    if response.status_code == 200:
                        result = self._parse_response(response.json())
                        if result:
                            logger.info(f"Success with model: {self.current_model}")
                            return result
                        else:
                            logger.warning("Empty response from API")
                            
                    elif response.status_code == 503:
                        # Model is loading
                        wait_time = 10 * (retry + 1)
                        logger.info(f"Model loading, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                        
                    elif response.status_code == 429:
                        # Rate limit
                        logger.warning("Rate limit hit. Waiting 30 seconds...")
                        time.sleep(30)
                        continue
                        
                    elif response.status_code == 422:
                        # Input too long
                        logger.warning("Input too long, reducing...")
                        prompt = prompt[:1000]  # Truncate prompt
                        continue
                        
                    else:
                        logger.error(f"API Error {response.status_code}: {response.text[:200]}")
                        break
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout on attempt {retry + 1}")
                    if retry == 2:
                        break
                    time.sleep(5 * (retry + 1))
                    
                except Exception as e:
                    logger.error(f"Request error: {e}")
                    break
            
            # Try next model if current failed
            if not self._try_next_model():
                break
        
        # All models failed
        error_msg = f"""
        ## ⚠️ AI Service Temporarily Unavailable
        
        **Reason:** All AI models are currently busy or your free tier limit may be reached.
        
        **Quick Fixes:**
        1. **Wait 1-2 minutes** and try again
        2. **Check your HuggingFace account** at: https://huggingface.co/settings/billing
        3. **Use smaller topic** for faster response
        
        **Trying:** {original_prompt}
        """
        return error_msg
    
    def _parse_response(self, response_data) -> Optional[str]:
        """Parse different response formats from HuggingFace"""
        try:
            if isinstance(response_data, list):
                if len(response_data) > 0:
                    item = response_data[0]
                    if isinstance(item, dict):
                        return item.get('generated_text', '')
                    else:
                        return str(item)
            
            elif isinstance(response_data, dict):
                return response_data.get('generated_text', '')
            
            # Try to convert whatever we got
            return str(response_data)[:1000]
            
        except:
            return None
    
    def extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        try:
            # Remove markdown code blocks
            clean_text = text.replace('```json', '').replace('```', '')
            
            # Find JSON
            start = clean_text.find('{')
            end = clean_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = clean_text[start:end]
                return json.loads(json_str)
            
            # Try array
            start = clean_text.find('[')
            end = clean_text.rfind(']') + 1
            
            if start >= 0 and end > start:
                json_str = clean_text[start:end]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error(f"JSON extraction error: {e}")
        
        return None