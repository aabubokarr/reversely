import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import pickle

# Import our updated utils
from utils import extract_features, search_similar_images

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/features', exist_ok=True)

# In-memory storage
image_features = {}
image_metadata = {}
next_image_id = 0

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    global next_image_id
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract features
            features = extract_features(filepath)
            image_id = next_image_id
            next_image_id += 1
            
            # Store features and metadata
            image_features[image_id] = features
            image_metadata[image_id] = {
                'filename': filename,
                'filepath': filepath
            }
            
            # Save features to disk
            try:
                with open(f'static/features/{image_id}.pkl', 'wb') as f:
                    pickle.dump(features, f)
            except Exception as e:
                print(f"Warning: Could not save features to disk: {e}")
            
            return jsonify({
                'message': 'Image uploaded successfully', 
                'image_id': image_id,
                'filename': filename
            })
    
    return render_template('upload.html')

@app.route('/search', methods=['GET', 'POST'])
def search_images():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save query image temporarily
            filename = secure_filename(file.filename)
            query_path = os.path.join(app.config['UPLOAD_FOLDER'], 'query_' + filename)
            file.save(query_path)
            
            # Extract features from query image
            query_features = extract_features(query_path)
            
            # Search for similar images
            similar_images = search_similar_images(query_features, image_features, image_metadata)
            
            # Remove temporary query file
            try:
                os.remove(query_path)
            except:
                pass
            
            return render_template('search_results.html', 
                                 query_image=filename,
                                 results=similar_images)
    
    return render_template('search.html')

@app.route('/images')
def list_images():
    """List all uploaded images"""
    images = []
    for img_id, meta in image_metadata.items():
        images.append({
            'id': img_id,
            'filename': meta['filename'],
            'has_features': image_features.get(img_id) is not None
        })
    return jsonify({'images': images, 'total': len(images)})

@app.route('/reset', methods=['POST'])
def reset_database():
    """Reset all uploaded images (for testing)"""
    global next_image_id
    image_features.clear()
    image_metadata.clear()
    next_image_id = 0
    
    # Clear feature files
    try:
        for file in os.listdir('static/features'):
            if file.endswith('.pkl'):
                os.remove(os.path.join('static/features', file))
    except Exception as e:
        print(f"Warning: Could not clear feature files: {e}")
    
    return jsonify({'message': 'Database reset successfully'})

if __name__ == '__main__':
    print("Starting Image Search Engine...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("Open http://localhost:5000 in your browser")
    
    # Try running with reloader disabled to avoid watchdog issues
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error: {e}")
        print("Trying without debug mode...")
        app.run(host='0.0.0.0', port=5000, debug=False)