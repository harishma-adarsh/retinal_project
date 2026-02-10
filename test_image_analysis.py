"""
Test script to analyze retinal images and show what the AI sees
"""
from PIL import Image
import numpy as np
import sys
import os

def analyze_image(image_path):
    """Analyze an image and show the statistics"""
    try:
        img = Image.open(image_path)
        
        # Apply the same cropping as the AI
        w, h = img.size
        left, top, right, bottom = w*0.2, h*0.2, w*0.8, h*0.8
        img_cropped = img.crop((left, top, right, bottom))
        
        img_gray = img_cropped.convert('L')
        pixels = np.array(img_gray)
        
        # Calculate the same stats as the AI
        std_dev = np.std(pixels)
        mean_val = np.mean(pixels)
        max_val = np.max(pixels)
        min_val = np.min(pixels)
        complexity_ratio = std_dev / (mean_val + 1)
        
        print(f"\n{'='*60}")
        print(f"Analyzing: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        print(f"Image Size: {w} x {h}")
        print(f"Cropped Size: {img_cropped.size}")
        print(f"\nPixel Statistics:")
        print(f"  Mean Brightness:    {mean_val:.2f}")
        print(f"  Std Deviation:      {std_dev:.2f}")
        print(f"  Min Value:          {min_val}")
        print(f"  Max Value:          {max_val}")
        print(f"  Complexity Ratio:   {complexity_ratio:.3f}")
        
        # Apply the current AI thresholds (from ml_utils.py)
        print(f"\nCurrent AI Thresholds:")
        print(f"  High Risk if: StdDev > 40.0 OR (Ratio > 1.0 AND StdDev > 39.5)")
        
        # Check the conditions
        condition1 = std_dev > 40.0
        condition2 = complexity_ratio > 1.0 and std_dev > 39.5
        
        print(f"\nCondition Checks:")
        print(f"  StdDev > 40.0:           {condition1} ({std_dev:.2f})")
        print(f"  Ratio > 1.0:             {complexity_ratio > 1.0} ({complexity_ratio:.3f})")
        print(f"  StdDev > 39.5:           {std_dev > 39.5} ({std_dev:.2f})")
        print(f"  Condition 2 (Both):      {condition2}")
        
        if condition1 or condition2:
            prediction = "HIGH RISK"
            color = "RED"
        else:
            prediction = "LOW RISK"
            color = "GREEN"
        
        print(f"\n{'='*60}")
        print(f"AI PREDICTION: {prediction}")
        print(f"{'='*60}\n")
        
        return {
            'std_dev': std_dev,
            'complexity_ratio': complexity_ratio,
            'prediction': prediction
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_image_analysis.py <image_path>")
        print("\nExample:")
        print("  python test_image_analysis.py path/to/retinal_scan.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"ERROR: File not found: {image_path}")
        sys.exit(1)
    
    analyze_image(image_path)
