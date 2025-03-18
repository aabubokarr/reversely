# Reverse Image Search Application

## Overview

This project provides a **Reverse Image Search** functionality where users can upload an image and receive a list of similar images based on the content of the uploaded image. The frontend is built using **HTML**, **CSS**, and **JavaScript** with **Ant Design** for UI components. The backend is developed in **Django** with a **TensorFlow MobileNet** model used for extracting image features and finding similar images based on cosine similarity.

## Features

- **Image Upload**: Allows users to upload an image for reverse image search.
- **Similar Images Display**: Displays images that are similar to the uploaded image, with a similarity score.
- **Image Preview**: View the uploaded and similar images in a preview modal without navigating to a new page.
- **Ant Design UI**: A modern, user-friendly interface using Ant Design components.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript, Ant Design (for UI components)
- **Backend**: Django, TensorFlow (MobileNet model), NumPy, SciPy
- **Image Processing**: TensorFlow MobileNet model for feature extraction and cosine similarity calculation
- **Image Storage**: Images are stored in Django's `MEDIA_ROOT` and uploaded to the server

## Backend Setup

The backend is responsible for processing the uploaded image, extracting features using the MobileNet model, and finding similar images based on those features.

### Requirements

- **Django**: Used to create the backend API and serve the frontend.
- **TensorFlow**: Used for image feature extraction via the MobileNet model.
- **NumPy**: For array handling during feature extraction.
- **SciPy**: To calculate cosine similarity between images.
- **Pillow (PIL)**: For loading and processing images.

### Installation and Configuration

1. **Install Dependencies**:

```bash
pip install django tensorflow numpy scipy pillow
