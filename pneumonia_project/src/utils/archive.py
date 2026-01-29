import os
import json
import hashlib
from datetime import datetime
from PIL import Image
from pathlib import Path

ARCHIVE_DIR = Path("/app/archive")


def compute_image_hash(image):
    """
    Compute MD5 hash of an image.

    Args:
        image: PIL Image or file-like object

    Returns:
        MD5 hash string
    """
    import io

    if isinstance(image, Image.Image):
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        content = buffer.getvalue()
    elif hasattr(image, 'read'):
        # File-like object
        pos = image.tell()
        content = image.read()
        image.seek(pos)  # Reset position
    else:
        content = image

    return hashlib.md5(content).hexdigest()


def get_archive_dir():
    """Get archive directory, create if not exists."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    return ARCHIVE_DIR


def generate_archive_id(filename):
    """Generate unique archive ID based on timestamp and filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c if c.isalnum() else "_" for c in Path(filename).stem)[:30]
    return f"{timestamp}_{safe_filename}"


def save_analysis(filename, original_img, processed_img, yolo_img, cls_data, detections, reasoning_data, metadata=None, image_hash=None):
    """
    Save an analysis to the archive.

    Args:
        filename: Original filename
        original_img: PIL Image (original)
        processed_img: PIL Image (CLAHE processed)
        yolo_img: PIL Image (with YOLO bounding boxes)
        cls_data: dict with is_positive, confidence
        detections: list of detection dicts
        reasoning_data: dict with steps and full_markdown
        metadata: optional dict with extra info (e.g., proiezione)
        image_hash: MD5 hash of the original image

    Returns:
        archive_id: The ID of the saved analysis
    """
    archive_dir = get_archive_dir()
    archive_id = generate_archive_id(filename)
    analysis_dir = archive_dir / archive_id
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Compute hash if not provided
    if image_hash is None and original_img:
        image_hash = compute_image_hash(original_img)

    # Save images
    if original_img:
        original_img.save(analysis_dir / "original.png")
    if processed_img:
        processed_img.save(analysis_dir / "processed.png")
    if yolo_img:
        yolo_img.save(analysis_dir / "yolo.png")

    # Save detection crops
    crops_dir = analysis_dir / "crops"
    crops_dir.mkdir(exist_ok=True)

    serializable_detections = []
    for i, det in enumerate(detections):
        det_copy = {k: v for k, v in det.items() if k != 'image_crop'}
        det_copy['crop_file'] = f"crop_{i+1}.png"
        serializable_detections.append(det_copy)

        if det.get('image_crop'):
            det['image_crop'].save(crops_dir / f"crop_{i+1}.png")

    # Prepare metadata JSON
    analysis_data = {
        "archive_id": archive_id,
        "filename": filename,
        "image_hash": image_hash,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cls_data": cls_data,
        "detections": serializable_detections,
        "reasoning_data": {
            "steps": [
                {k: v for k, v in step.items() if k != 'image'}
                for step in reasoning_data.get('steps', [])
            ],
            "full_markdown": reasoning_data.get('full_markdown', '')
        },
        "metadata": metadata or {}
    }

    with open(analysis_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)

    return archive_id


def list_analyses():
    """
    List all saved analyses.

    Returns:
        List of dicts with archive_id, filename, timestamp, is_positive
    """
    archive_dir = get_archive_dir()
    analyses = []

    for entry in sorted(archive_dir.iterdir(), reverse=True):
        if entry.is_dir():
            metadata_file = entry / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    analyses.append({
                        "archive_id": data.get("archive_id", entry.name),
                        "filename": data.get("filename", "Unknown"),
                        "timestamp": data.get("timestamp", ""),
                        "is_positive": data.get("cls_data", {}).get("is_positive", False),
                        "confidence": data.get("cls_data", {}).get("confidence", 0),
                        "num_detections": len(data.get("detections", []))
                    })
                except (json.JSONDecodeError, KeyError):
                    pass

    return analyses


def load_analysis(archive_id):
    """
    Load a saved analysis.

    Args:
        archive_id: The ID of the analysis to load

    Returns:
        dict with all analysis data and images, or None if not found
    """
    archive_dir = get_archive_dir()
    analysis_dir = archive_dir / archive_id

    if not analysis_dir.exists():
        return None

    metadata_file = analysis_dir / "metadata.json"
    if not metadata_file.exists():
        return None

    with open(metadata_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load images
    original_path = analysis_dir / "original.png"
    processed_path = analysis_dir / "processed.png"
    yolo_path = analysis_dir / "yolo.png"

    data['original_img'] = Image.open(original_path) if original_path.exists() else None
    data['processed_img'] = Image.open(processed_path) if processed_path.exists() else None
    data['yolo_img'] = Image.open(yolo_path) if yolo_path.exists() else None

    # Load detection crops
    crops_dir = analysis_dir / "crops"
    for det in data.get('detections', []):
        crop_file = det.get('crop_file')
        if crop_file:
            crop_path = crops_dir / crop_file
            if crop_path.exists():
                det['image_crop'] = Image.open(crop_path)

    # Rebuild reasoning_data steps with images if needed
    for step in data.get('reasoning_data', {}).get('steps', []):
        step['image'] = None  # Images in steps are crops, handled via detections

    return data


def is_already_archived(image_hash):
    """
    Check if an analysis with this image hash already exists.

    Args:
        image_hash: MD5 hash of the image

    Returns:
        archive_id if exists, None otherwise
    """
    archive_dir = get_archive_dir()

    for entry in archive_dir.iterdir():
        if entry.is_dir():
            metadata_file = entry / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("image_hash") == image_hash:
                        return data.get("archive_id", entry.name)
                except (json.JSONDecodeError, KeyError):
                    pass
    return None


def delete_analysis(archive_id):
    """
    Delete a saved analysis.

    Args:
        archive_id: The ID of the analysis to delete

    Returns:
        True if deleted, False if not found
    """
    import shutil
    archive_dir = get_archive_dir()
    analysis_dir = archive_dir / archive_id

    if analysis_dir.exists():
        shutil.rmtree(analysis_dir)
        return True
    return False
