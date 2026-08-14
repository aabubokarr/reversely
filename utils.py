import os

import cv2
import numpy as np


# ============================================================
# SCAN MEDIA DIRECTORY
# ============================================================

def scan_media_directory(
    media_folder,
    allowed_extensions
):
    """
    Recursively find supported image files.
    """

    image_files = []

    if not os.path.exists(
        media_folder
    ):

        return image_files

    for root, dirs, files in os.walk(
        media_folder
    ):

        for filename in files:

            if "." not in filename:
                continue

            extension = filename.rsplit(
                ".",
                1
            )[1].lower()

            if extension in allowed_extensions:

                filepath = os.path.join(
                    root,
                    filename
                )

                image_files.append(
                    filepath
                )

    image_files.sort()

    return image_files


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(image_path):
    """
    Extract traditional computer vision features.

    Features:

    1. HSV color histogram
    2. Spatial color histogram
    3. LBP texture
    4. Edge information
    5. Hu shape moments
    """

    try:

        image = cv2.imread(
            image_path
        )

        if image is None:

            print(
                f"Could not read: {image_path}"
            )

            return None

        # ----------------------------------------------------
        # Normalize image size
        # ----------------------------------------------------

        image = cv2.resize(
            image,
            (224, 224),
            interpolation=cv2.INTER_AREA
        )

        # ----------------------------------------------------
        # HSV
        # ----------------------------------------------------

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV
        )

        # ----------------------------------------------------
        # Global color histograms
        # ----------------------------------------------------

        color_features = []

        hsv_config = [
            (0, 32, [0, 180]),
            (1, 32, [0, 256]),
            (2, 32, [0, 256])
        ]

        for channel, bins, value_range in hsv_config:

            histogram = cv2.calcHist(
                [hsv],
                [channel],
                None,
                [bins],
                value_range
            )

            histogram = cv2.normalize(
                histogram,
                histogram
            )

            color_features.append(
                histogram.flatten().astype(
                    np.float32
                )
            )

        # ----------------------------------------------------
        # Spatial color
        # ----------------------------------------------------

        spatial_features = []

        height, width = hsv.shape[:2]

        regions = [
            hsv[
                :height // 2,
                :width // 2
            ],

            hsv[
                :height // 2,
                width // 2:
            ],

            hsv[
                height // 2:,
                :width // 2
            ],

            hsv[
                height // 2:,
                width // 2:
            ]
        ]

        for region in regions:

            histogram = cv2.calcHist(
                [region],
                [0, 1],
                None,
                [16, 16],
                [0, 180, 0, 256]
            )

            histogram = cv2.normalize(
                histogram,
                histogram
            )

            spatial_features.append(
                histogram.flatten().astype(
                    np.float32
                )
            )

        # ----------------------------------------------------
        # Grayscale
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # ----------------------------------------------------
        # LBP
        # ----------------------------------------------------

        lbp = local_binary_pattern(
            gray
        )

        lbp_histogram, _ = np.histogram(
            lbp.ravel(),
            bins=256,
            range=(0, 256)
        )

        lbp_histogram = lbp_histogram.astype(
            np.float32
        )

        lbp_histogram /= (
            lbp_histogram.sum()
            + 1e-8
        )

        # ----------------------------------------------------
        # Edges
        # ----------------------------------------------------

        edges = cv2.Canny(
            gray,
            100,
            200
        )

        edge_density = (
            np.count_nonzero(edges)
            / edges.size
        )

        edge_histogram = cv2.calcHist(
            [edges],
            [0],
            None,
            [32],
            [0, 256]
        )

        edge_histogram = cv2.normalize(
            edge_histogram,
            edge_histogram
        ).flatten()

        edge_histogram = edge_histogram.astype(
            np.float32
        )

        # ----------------------------------------------------
        # Hu moments
        # ----------------------------------------------------

        moments = cv2.moments(
            gray
        )

        hu = cv2.HuMoments(
            moments
        ).flatten()

        hu = np.array(
            [
                (
                    -np.sign(value)
                    * np.log10(abs(value))
                )
                if value != 0
                else 0.0
                for value in hu
            ],
            dtype=np.float32
        )

        # ----------------------------------------------------
        # Return feature groups
        # ----------------------------------------------------

        return {
            "color": color_features,
            "spatial_color": spatial_features,
            "lbp": lbp_histogram,
            "edge_density": float(
                edge_density
            ),
            "edge_hist": edge_histogram,
            "hu": hu
        }

    except Exception as e:

        print(
            f"Feature extraction error "
            f"for {image_path}: {e}"
        )

        return None


# ============================================================
# LOCAL BINARY PATTERN
# ============================================================

def local_binary_pattern(
    image,
    points=8,
    radius=1
):
    """
    Fast 8-neighbor LBP implementation.
    """

    gray = image

    if len(gray.shape) > 2:

        gray = cv2.cvtColor(
            gray,
            cv2.COLOR_BGR2GRAY
        )

    gray = gray.astype(
        np.uint8
    )

    height, width = gray.shape

    lbp = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    center = gray[
        1:height - 1,
        1:width - 1
    ]

    neighbors = [
        (-1, -1),
        (-1,  0),
        (-1,  1),
        ( 0,  1),
        ( 1,  1),
        ( 1,  0),
        ( 1, -1),
        ( 0, -1)
    ]

    for bit, (dy, dx) in enumerate(
        neighbors
    ):

        neighbor = gray[
            1 + dy:height - 1 + dy,
            1 + dx:width - 1 + dx
        ]

        lbp[
            1:height - 1,
            1:width - 1
        ] |= (
            (
                neighbor >= center
            ).astype(
                np.uint8
            ) << bit
        )

    return lbp


# ============================================================
# HISTOGRAM SIMILARITY
# ============================================================

def histogram_similarity(
    histogram1,
    histogram2
):
    """
    Compare two histograms.

    Returns a value between 0 and 1.
    """

    try:

        distance = cv2.compareHist(
            histogram1.astype(
                np.float32
            ),
            histogram2.astype(
                np.float32
            ),
            cv2.HISTCMP_BHATTACHARYYA
        )

        similarity = 1.0 - min(
            distance,
            1.0
        )

        return float(
            max(
                similarity,
                0.0
            )
        )

    except Exception:

        return 0.0


# ============================================================
# TEXTURE SIMILARITY
# ============================================================

def texture_similarity(
    histogram1,
    histogram2
):
    """
    Chi-square based texture similarity.
    """

    denominator = (
        histogram1
        + histogram2
        + 1e-10
    )

    distance = 0.5 * np.sum(
        (
            (histogram1 - histogram2) ** 2
        )
        / denominator
    )

    similarity = np.exp(
        -distance
    )

    return float(
        np.clip(
            similarity,
            0.0,
            1.0
        )
    )


# ============================================================
# SHAPE SIMILARITY
# ============================================================

def shape_similarity(
    hu1,
    hu2
):
    """
    Compare Hu moments.
    """

    distance = np.mean(
        np.abs(
            hu1 - hu2
        )
    )

    similarity = np.exp(
        -distance
    )

    return float(
        np.clip(
            similarity,
            0.0,
            1.0
        )
    )


# ============================================================
# COMPLETE IMAGE SIMILARITY
# ============================================================

def calculate_similarity(
    query,
    candidate
):
    """
    Calculate a balanced similarity score.

    Color is intentionally prevented from dominating
    the entire result.
    """

    # --------------------------------------------------------
    # Global color
    # --------------------------------------------------------

    color_scores = []

    for query_hist, candidate_hist in zip(
        query["color"],
        candidate["color"]
    ):

        color_scores.append(
            histogram_similarity(
                query_hist,
                candidate_hist
            )
        )

    color_score = float(
        np.mean(color_scores)
    )

    # --------------------------------------------------------
    # Spatial color
    # --------------------------------------------------------

    spatial_scores = []

    for query_hist, candidate_hist in zip(
        query["spatial_color"],
        candidate["spatial_color"]
    ):

        spatial_scores.append(
            histogram_similarity(
                query_hist,
                candidate_hist
            )
        )

    spatial_score = float(
        np.mean(spatial_scores)
    )

    # --------------------------------------------------------
    # Texture
    # --------------------------------------------------------

    texture_score = texture_similarity(
        query["lbp"],
        candidate["lbp"]
    )

    # --------------------------------------------------------
    # Edge
    # --------------------------------------------------------

    edge_hist_score = histogram_similarity(
        query["edge_hist"],
        candidate["edge_hist"]
    )

    edge_density_difference = abs(
        query["edge_density"]
        - candidate["edge_density"]
    )

    edge_density_score = 1.0 - min(
        edge_density_difference * 10.0,
        1.0
    )

    edge_score = (
        edge_hist_score * 0.7
        +
        edge_density_score * 0.3
    )

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    shape_score = shape_similarity(
        query["hu"],
        candidate["hu"]
    )

    # --------------------------------------------------------
    # FINAL WEIGHTED SCORE
    # --------------------------------------------------------

    score = (
        color_score * 0.25
        +
        spatial_score * 0.25
        +
        texture_score * 0.20
        +
        edge_score * 0.15
        +
        shape_score * 0.15
    )

    return float(
        np.clip(
            score,
            0.0,
            1.0
        )
    )


# ============================================================
# SEARCH
# ============================================================

def search_similar_images(
    query_features,
    image_features,
    image_metadata,
    top_k=50,
    threshold=0.80
):
    """
    Search the indexed media collection.

    Only images above the threshold are returned.
    """

    if query_features is None:
        return []

    if not image_features:
        return []

    results = []

    for image_id, features in image_features.items():

        if features is None:
            continue

        try:

            score = calculate_similarity(
                query_features,
                features
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Weak matches are discarded.
            # ------------------------------------------------

            if score < threshold:
                continue

            metadata = image_metadata.get(
                image_id
            )

            if metadata is None:
                continue

            results.append({
                "image_id": image_id,
                "similarity": score,
                "filename": metadata[
                    "filename"
                ],
                "relative_path": metadata[
                    "relative_path"
                ]
            })

        except Exception as e:

            print(
                f"Error comparing image "
                f"{image_id}: {e}"
            )

    results.sort(
        key=lambda item:
        item["similarity"],
        reverse=True
    )

    return results[:top_k]
