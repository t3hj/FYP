"""
AI-powered image analysis for Local Lens application.
Includes Ollama LLaVA integration and simple fallback analysis.
"""
import base64
import io
import requests
from PIL import Image
from config import ISSUE_CATEGORIES


def analyze_image_with_ai(uploaded_file):
    """Use AI to analyze image and suggest category - tries multiple free options
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Suggested category or None
    """
    # Try Ollama first (local, free, unlimited)
    category = try_ollama_analysis(uploaded_file)
    if category:
        return category
    
    # Fallback to simple image analysis (always works, no external deps)
    category = try_simple_image_analysis(uploaded_file)
    if category:
        return category
    
    return None


def try_ollama_analysis(uploaded_file):
    """Try Ollama LLaVA for local AI analysis (100% free, no limits)"""
    try:
        # Check if Ollama is running locally
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            return None
        
        # Check if llava model is available
        models = response.json().get("models", [])
        if not any("llava" in m.get("name", "").lower() for m in models):
            return None
        
        # Read image
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        
        # Convert to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create prompt
        categories_str = ", ".join(ISSUE_CATEGORIES)
        prompt = f"""Analyze this image and determine which community issue category it best fits.

Available categories: {categories_str}

Look for:
- Pothole: Damaged road surface, holes in pavement
- Broken Streetlight: Non-functioning street lamps, damaged light fixtures
- Graffiti: Spray paint, unauthorized markings on walls/surfaces
- Litter: Trash, garbage on streets or public areas
- Damaged Road Sign: Bent, broken, or missing traffic signs
- Other: Any other community issues not listed above

Respond with ONLY the category name that best matches, nothing else."""

        # Call Ollama API with longer timeout (model may need to load)
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llava",
                "prompt": prompt,
                "images": [image_b64],
                "stream": False
            },
            timeout=120  # Increased timeout for model loading
        )
        
        if ollama_response.status_code == 200:
            result = ollama_response.json()
            suggested_category = result.get("response", "").strip()
            
            # Validate the response
            if suggested_category in ISSUE_CATEGORIES:
                return suggested_category
            
            # Try to match partial responses
            for category in ISSUE_CATEGORIES:
                if category.lower() in suggested_category.lower():
                    return category
        
        return None
    
    except Exception:
        return None


def try_simple_image_analysis(uploaded_file):
    """Simple image analysis using color and texture patterns (always works)
    
    This is a basic heuristic classifier that analyzes image characteristics
    to suggest a category. It's not as accurate as AI but works instantly.
    """
    try:
        # Read image
        uploaded_file.seek(0)
        image = Image.open(io.BytesIO(uploaded_file.read()))
        uploaded_file.seek(0)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for faster processing
        image = image.resize((100, 100))
        pixels = list(image.getdata())
        
        # Analyze color distribution
        total_pixels = len(pixels)
        
        # Count color categories
        dark_count = 0  # For potholes (dark areas)
        bright_count = 0  # For streetlights
        colorful_count = 0  # For graffiti (vibrant colors)
        brown_green_count = 0  # For litter in outdoor settings
        red_yellow_count = 0  # For road signs
        gray_count = 0  # For roads/pavement
        
        for r, g, b in pixels:
            brightness = (r + g + b) / 3
            saturation = max(r, g, b) - min(r, g, b)
            
            # Dark pixels (potential pothole)
            if brightness < 60:
                dark_count += 1
            
            # Very bright pixels (potential streetlight)
            if brightness > 200:
                bright_count += 1
            
            # Colorful/vibrant (potential graffiti)
            if saturation > 100 and brightness > 50 and brightness < 200:
                colorful_count += 1
            
            # Brown/green tones (outdoor litter setting)
            if (g > r and g > b) or (r > 100 and g > 70 and b < 100):
                brown_green_count += 1
            
            # Red/yellow (road signs)
            if (r > 180 and g < 100 and b < 100) or (r > 180 and g > 150 and b < 100):
                red_yellow_count += 1
            
            # Gray (pavement/road)
            if saturation < 30 and 60 < brightness < 180:
                gray_count += 1
        
        # Calculate percentages
        dark_pct = dark_count / total_pixels
        bright_pct = bright_count / total_pixels
        colorful_pct = colorful_count / total_pixels
        red_yellow_pct = red_yellow_count / total_pixels
        gray_pct = gray_count / total_pixels
        
        # Decision logic based on color analysis
        scores = {
            'Pothole': dark_pct * 0.5 + gray_pct * 0.3,
            'Broken Streetlight': bright_pct * 0.4 + dark_pct * 0.2,
            'Graffiti': colorful_pct * 0.6,
            'Litter': brown_green_count / total_pixels * 0.3,
            'Damaged Road Sign': red_yellow_pct * 0.5,
            'Other': 0.1  # Default low score
        }
        
        # Get best match
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        
        # Only return if we have reasonable confidence
        if best_score > 0.15:
            return best_category
        
        return 'Other'
    
    except Exception:
        return None


def check_ollama_status():
    """Check if Ollama is running and LLaVA model is available
    
    Returns:
        tuple: (is_running: bool, has_llava: bool, message: str)
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            has_llava = any("llava" in m.get("name", "").lower() for m in models)
            if has_llava:
                return True, True, "Ollama LLaVA Ready"
            else:
                return True, False, "Ollama running (no LLaVA)"
        return False, False, "Ollama not responding"
    except:
        return False, False, "Using basic analysis"
