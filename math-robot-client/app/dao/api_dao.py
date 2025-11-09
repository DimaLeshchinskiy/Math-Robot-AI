import requests
import base64
from config import config

class ApiDAO:
    """Data Access Object for Math Robot API communication"""
    
    _base_url = config.API_BASE_URL
    _auth = (config.API_USERNAME, config.API_PASSWORD)
    
    @staticmethod
    def send_image_data(image_bytes, width, height, colorspace=13):
        """
        Send image bytes directly to API for processing
        
        Args:
            image_bytes: Raw image bytes from robot camera
            width: Image width
            height: Image height
            colorspace: Image colorspace (13=RGB, 17=Depth)
            
        Returns:
            Dictionary with API response data
        """
        try:
            # Convert image bytes to base64 for API transmission
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            payload = {
                'image_data': image_b64,
                'width': width,
                'height': height,
                'colorspace': colorspace,
                'target_regions': config.API_TARGET_REGIONS
            }
            
            response = requests.post(
                f"{ApiDAO._base_url}/pipeline",
                json=payload,
                auth=ApiDAO._auth,
                timeout=30
            )
                
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}",
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    @staticmethod
    def health_check():
        """Check if API is available"""
        try:
            response = requests.get(f"{ApiDAO._base_url}/status", auth=ApiDAO._auth, timeout=10)
            return response.status_code == 200
        except:
            return False