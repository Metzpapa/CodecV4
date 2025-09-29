# custom_tools.py

import base64
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display
import cv2  # OpenCV for video processing

from claude_agent_sdk import tool

# A temporary directory to store generated images for viewing.
# This keeps the agent's primary workspace clean.
VIEW_CACHE_DIR = Path("./.view_cache")
VIEW_CACHE_DIR.mkdir(exist_ok=True)

def file_to_base64_image_content(image_path: Path, media_type: str) -> dict:
    """
    Reads an image file and encodes it into the base64 format required by the Claude API.

    Args:
        image_path: The path to the image file.
        media_type: The MIME type of the image (e.g., "image/png", "image/jpeg").

    Returns:
        A dictionary formatted as a Claude API image content block.
    """
    with open(image_path, "rb") as f:
        encoded_data = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": encoded_data,
        }
    }

@tool(
    "view_media",
    "Displays a visual representation of a media file (image, audio, or video). For videos, it shows the middle frame. For audio, it shows a spectrogram.",
    {"file_path": str}
)
async def view_media(args: dict) -> dict:
    """
    Takes a file path and returns a visual representation for the LLM.
    - For images, it returns the image directly.
    - For audio, it generates and returns a spectrogram.
    - For video, it extracts and returns the middle frame.
    """
    try:
        file_path = Path(args["file_path"])
        if not file_path.exists():
            return {
                "content": [{"type": "text", "text": f"Error: File not found at '{file_path}'"}],
                "is_error": True
            }

        suffix = file_path.suffix.lower()
        content_blocks = []

        if suffix in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
            media_type = f"image/{'jpeg' if suffix == '.jpg' else suffix[1:]}"
            content_blocks.append({"type": "text", "text": f"Displaying image: {file_path.name}"})
            content_blocks.append(file_to_base64_image_content(file_path, media_type))

        elif suffix in ['.wav', '.mp3', '.flac', '.m4a']:
            output_path = VIEW_CACHE_DIR / f"{file_path.stem}_spectrogram.png"
            
            y, sr = librosa.load(file_path)
            D = librosa.stft(y)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            
            fig, ax = plt.subplots(figsize=(10, 4))
            librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', ax=ax)
            ax.set_title(f'Spectrogram of {file_path.name}')
            fig.tight_layout()
            
            plt.savefig(output_path)
            plt.close(fig)
            
            content_blocks.append({"type": "text", "text": f"Generated spectrogram for audio file: {file_path.name}"})
            content_blocks.append(file_to_base64_image_content(output_path, "image/png"))

        elif suffix in ['.mp4', '.mov', '.avi', '.mkv']:
            output_path = VIEW_CACHE_DIR / f"{file_path.stem}_middle_frame.jpg"
            
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise IOError(f"Cannot open video file: {file_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            middle_frame_index = total_frames // 2
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise ValueError(f"Could not read middle frame from {file_path.name}")
            
            cv2.imwrite(str(output_path), frame)
            
            content_blocks.append({"type": "text", "text": f"Extracted middle frame from video file: {file_path.name}"})
            content_blocks.append(file_to_base64_image_content(output_path, "image/jpeg"))

        else:
            return {
                "content": [{"type": "text", "text": f"Error: Unsupported file type '{suffix}' for viewing."}],
                "is_error": True
            }

        return {"content": content_blocks}

    except Exception as e:
        error_message = f"An error occurred while trying to view '{args.get('file_path', 'unknown file')}': {str(e)}"
        return {
            "content": [{"type": "text", "text": error_message}],
            "is_error": True
        }