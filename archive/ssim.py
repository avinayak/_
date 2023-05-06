import itertools
from skimage import io, metrics
from PIL import Image
import numpy as np
from pathlib import Path
from random import shuffle
import multiprocessing
from tqdm import tqdm
import sys

required_extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]
image_paths = []
for paths in [Path('docs/images').rglob(ext) for ext in required_extensions]:
    for path in list(paths):
        image_paths.append(path.relative_to('.'))
shuffle(image_paths)


def load_and_resize_image(image_path, size=(256, 256)):
    img = Image.open(image_path)
    # convert to RGBA
    img = img.convert("RGBA")
    img = img.resize(size, Image.ANTIALIAS)
    return np.asarray(img)


def compare_images(image1_path, image2_path):
    image1 = load_and_resize_image(image1_path)
    image2 = load_and_resize_image(image2_path)

    similarity = metrics.structural_similarity(
        image1, image2, multichannel=True, channel_axis=2)
    return similarity


def compare_image_pair(image_pair):
    i1, i2 = image_pair
    return i1, i2, compare_images(i1, i2)


def sort_images_by_similarity(image_paths):
    image_pairs = list(itertools.combinations(image_paths, 2))

    with multiprocessing.Pool(processes=int(sys.argv[1])) as pool:
        # similarities = pool.map(compare_image_pair, image_pairs)
        similarities = list(
            tqdm(pool.imap(compare_image_pair, image_pairs), total=len(image_pairs)))

    similarities.sort(key=lambda x: x[2], reverse=True)

    sorted_image_paths = [similarities[0][0]]
    for _, i2, _ in similarities:
        if i2 not in sorted_image_paths:
            sorted_image_paths.append(i2)

    return sorted_image_paths


if __name__ == "__main__":
    shuffle(image_paths)
    image_paths = image_paths
    sorted_images = sort_images_by_similarity(image_paths)
    print("Sorted images by similarity:")
    for img in sorted_images:
        print(img)
    # write all images to files with index in name to folder ordered
    for i, img in enumerate(sorted_images):
        with open(f"ordered/{i:03d}.jpg", "wb") as f:
            f.write(img.read_bytes())
