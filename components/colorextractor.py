#File holdilg all the pallete extrating logic 
import numpy as np

from components.photoupload import load_image, to_array

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(int(v) for v in rgb))


def extract_palette(source, n_colors=5, step=32):
    """Return the n most common colors, most common first.

    step is the bucket width: bigger = broader color groups
    (64 = low detail, 32 = medium, 16 = high).
    Each result: {"hex": "#rrggbb", "rgb": [r, g, b], "percent": float}
    """
    image = load_image(source, max_size=150)  # small = fast, less noise
    pixels = to_array(image).reshape(-1, 3).astype(int)  # (H*W, 3)

    # Snap each channel to the middle of its bucket so similar colors match
    quantized = (pixels // step) * step + step // 2

    colors, counts = np.unique(quantized, axis=0, return_counts=True)
    order = np.argsort(counts)[::-1][:n_colors]
    total = counts.sum()

    return [
        {
            "hex": rgb_to_hex(colors[i]),
            "rgb": [int(v) for v in colors[i]],
            "percent": round(float(counts[i] / total * 100), 1),
        }
        for i in order
    ]


def sample_patch(arr, x, y, r=2):
    """Average color around pixel (x, y) in an (H, W, 3) array.

    r=2 averages a 5x5 patch, which is steadier than a single noisy pixel.
    Use this for click-to-sample.
    """
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(f"sample_patch expects (H, W, 3), got {arr.shape}")
    h, w, _ = arr.shape
    x = min(max(int(x), 0), w - 1)
    y = min(max(int(y), 0), h - 1)
    patch = arr[max(y - r, 0):y + r + 1, max(x - r, 0):x + r + 1]
    R, G, B = patch.reshape(-1, 3).mean(axis=0).round().astype(int)
    return {"x": x, "y": y, "rgb": [int(R), int(G), int(B)],
            "hex": rgb_to_hex((R, G, B))}


# Quick test: python colorextraction.py path/to/photo.jpg
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python colorextraction.py path/to/image")
        sys.exit(1)
    for c in extract_palette(sys.argv[1]):
        print(c)