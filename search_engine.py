import os
import pickle
from pathlib import Path

import numpy as np
import torch
import open_clip
from PIL import Image


INDEX_FILE = "image_index.pkl"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
}


class ImageSearchEngine:

    def __init__(self):

        # Apple Silicon GPU when available
        if torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

        print("Device:", self.device)

        print("Loading vision model...")

        self.model, _, self.preprocess = (
            open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k"
            )
        )

        self.model = self.model.to(self.device)
        self.model.eval()

        self.index = []

        self.load_index()

    # ---------------------------------------------------------
    # INDEX
    # ---------------------------------------------------------

    def load_index(self):

        if not os.path.exists(INDEX_FILE):
            return

        try:

            with open(INDEX_FILE, "rb") as f:
                self.index = pickle.load(f)

            # Remove entries whose files no longer exist
            self.index = [
                item
                for item in self.index
                if os.path.exists(item["path"])
            ]

            print(
                f"Loaded {len(self.index):,} indexed images"
            )

        except Exception as e:

            print("Could not load index:", e)
            self.index = []

    def save_index(self):

        try:

            with open(INDEX_FILE, "wb") as f:
                pickle.dump(
                    self.index,
                    f,
                    protocol=pickle.HIGHEST_PROTOCOL
                )

        except Exception as e:

            print("Could not save index:", e)

    # ---------------------------------------------------------
    # FIND IMAGES
    # ---------------------------------------------------------

    def find_images(self, folder):

        folder = Path(folder)

        images = []

        for path in folder.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            images.append(str(path))

        return images

    # ---------------------------------------------------------
    # EMBEDDING
    # ---------------------------------------------------------

    def get_embedding(self, image_path):

        try:

            image = Image.open(
                image_path
            ).convert("RGB")

            image_tensor = self.preprocess(
                image
            ).unsqueeze(0)

            image_tensor = image_tensor.to(
                self.device
            )

            with torch.no_grad():

                embedding = self.model.encode_image(
                    image_tensor
                )

                embedding = embedding / embedding.norm(
                    dim=-1,
                    keepdim=True
                )

            return embedding.cpu().numpy()[0].astype(
                np.float32
            )

        except Exception as e:

            print(
                f"Could not process {image_path}: {e}"
            )

            return None

    # ---------------------------------------------------------
    # BUILD INDEX
    # ---------------------------------------------------------

    def build_index(
        self,
        folder,
        progress_callback=None
    ):

        image_paths = self.find_images(folder)

        total = len(image_paths)

        new_index = []

        for number, path in enumerate(
            image_paths,
            start=1
        ):

            embedding = self.get_embedding(path)

            if embedding is not None:

                new_index.append({
                    "path": path,
                    "embedding": embedding
                })

            if progress_callback:

                progress_callback(
                    number,
                    total,
                    path
                )

        self.index = new_index

        self.save_index()

        return len(new_index)

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(
        self,
        query_path,
        threshold=0.80,
        top_k=50
    ):

        if not self.index:
            return []

        query_embedding = self.get_embedding(
            query_path
        )

        if query_embedding is None:
            return []

        results = []

        # Since embeddings are normalized,
        # cosine similarity is simply a dot product.
        query = query_embedding

        for item in self.index:

            path = item["path"]

            # Don't return the query itself
            try:

                if os.path.samefile(
                    path,
                    query_path
                ):
                    continue

            except (FileNotFoundError, OSError):

                if os.path.abspath(path) == os.path.abspath(
                    query_path
                ):
                    continue

            embedding = item["embedding"]

            similarity = float(
                np.dot(
                    query,
                    embedding
                )
            )

            if similarity >= threshold:

                results.append({
                    "path": path,
                    "similarity": similarity
                })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results[:top_k]
    