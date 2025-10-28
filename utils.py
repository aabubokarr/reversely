import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import os

def extract_features(image_path):
    """Extract features using OpenCV and traditional computer vision methods"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        # Resize for consistency
        img = cv2.resize(img, (224, 224))
        
        features = []
        
        # 1. Color Histogram Features (RGB)
        for i in range(3):
            hist = cv2.calcHist([img], [i], None, [64], [0, 256])
            cv2.normalize(hist, hist)
            features.extend(hist.flatten())
        
        # 2. HSV Color Histogram
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        for i in range(3):
            hist = cv2.calcHist([hsv], [i], None, [32], [0, 256])
            cv2.normalize(hist, hist)
            features.extend(hist.flatten())
        
        # 3. Texture Features using LBP (Local Binary Patterns)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lbp = local_binary_pattern(gray)
        lbp_hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        lbp_hist = lbp_hist.astype(float)
        lbp_hist /= (lbp_hist.sum() + 1e-8)  # Normalize
        features.extend(lbp_hist.flatten())
        
        # 4. Edge Features using Canny
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (edges.size * 255)
        features.append(edge_density)
        
        # 5. Shape Moments
        moments = cv2.moments(gray)
        hu_moments = cv2.HuMoments(moments).flatten()
        features.extend(hu_moments)
        
        return np.array(features)
        
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return None

def local_binary_pattern(image, points=8, radius=1):
    """Calculate Local Binary Pattern"""
    try:
        # Simple LBP implementation
        gray = image
        if len(image.shape) > 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
        lbp = np.zeros_like(gray)
        for i in range(radius, gray.shape[0]-radius):
            for j in range(radius, gray.shape[1]-radius):
                center = gray[i,j]
                binary = ''
                # Simple 3x3 neighborhood
                for x in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        if x == 0 and y == 0:
                            continue
                        neighbor = gray[i+x, j+y]
                        binary += '1' if neighbor >= center else '0'
                # Convert binary to decimal
                lbp[i,j] = int(binary, 2)
        return lbp
    except:
        # Fallback: return zeros
        return np.zeros_like(image)

def search_similar_images(query_features, image_features, image_metadata, top_k=10):
    """Search for similar images based on feature similarity"""
    if query_features is None or not image_features:
        return []
    
    similarities = []
    
    for img_id, features in image_features.items():
        if features is not None:
            try:
                # Ensure both feature vectors have same length
                min_len = min(len(query_features), len(features))
                query_truncated = query_features[:min_len]
                features_truncated = features[:min_len]
                
                # Calculate cosine similarity
                sim = cosine_similarity([query_truncated], [features_truncated])[0][0]
                similarities.append((img_id, sim))
            except Exception as e:
                print(f"Error calculating similarity for image {img_id}: {e}")
                continue
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k results
    results = []
    for img_id, similarity in similarities[:top_k]:
        results.append({
            'image_id': img_id,
            'similarity': float(similarity),
            'filename': image_metadata[img_id]['filename'],
            'filepath': image_metadata[img_id]['filepath']
        })
    
    return results