"""A MoodBoard generator by atul"""

import os
import hashlib
import multiprocessing

from pathlib import Path
from random import choice, shuffle
from dataclasses import dataclass, field
from PIL import Image

import imagehash
import jinja2
from tqdm import tqdm
from functools import wraps
from time import time
from colorthief import ColorThief

required_extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]
NUM_IMAGES_PER_PAGE = 100


@dataclass(order=True)
class UnderscoreImage:
    """ Image class """
    sort_index: int = field(init=False)
    path: str
    html_path: str
    file_hash: str
    phash: str
    meta: str

    def __post_init__(self):
        self.sort_index = self.phash


ignored_files = []
with open("ignore.txt", "r") as f:
    ignored_files = f.read().splitlines()


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r  took: %2.4f sec' %
              (f.__name__, te-ts))
        return result
    return wrap


def get_dominant_color(img):
    color_thief = ColorThief(img)
    return color_thief.get_color(quality=1)


def generate_hash(filename: str) -> str:
    """Generate a hash of the file"""
    with open(filename, 'rb') as imagefile:
        return hashlib.md5(imagefile.read()).hexdigest()


def chunks(lst, n_chunks):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n_chunks):
        yield lst[i:i + n_chunks]


def file_extension(filepath: str):
    """ Get the file extension of a file """
    return os.path.splitext(filepath)[1]


def meta_alt(image):
    """ Get the alt of an image """
    return str(image).split("_")[-1].split(".")[0]


def calculate_perceptural_hash(image):
    """ Calculate the perceptual hash of an image """
    pil_image = open_image(image)
    return imagehash.colorhash(pil_image, binbits=32)


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def generate_thumbnail_if_not_exists(imagedata):
    """ Generate a thumbnail for an image """
    thumbfilepath = "./docs/thumbnails/" + imagedata.file_hash + ".jpg"
    if not os.path.exists(thumbfilepath):
        im = open_image(imagedata.path)
        im_thumb = crop_max_square(im).resize((50, 50), Image.LANCZOS)
        im_thumb.save(thumbfilepath, optimize=True, quality=20)


def generaate_image_metadata(image_path) -> UnderscoreImage:
    """ Generate metadata for an image """
    meta = meta_alt(image_path)
    file_hash = generate_hash(image_path)
    if file_hash in ignored_files:
        return None
    html_path = image_path.relative_to(Path("./docs")).as_posix()
    phash = calculate_perceptural_hash(image_path)
    return UnderscoreImage(image_path, html_path, file_hash, phash, meta)


@timing
def dedupe(imagedata):
    deduped_list = []
    seen_hashes = set()
    for image in imagedata:
        if image is not None:
            if image.file_hash not in seen_hashes:
                seen_hashes.add(image.file_hash)
                deduped_list.append(image)
    return deduped_list


@timing
def generate_dominant_colors(imagedata):
    return [get_dominant_color(imageset[0].path) for _, imageset in (enumerate(chunks(imagedata, NUM_IMAGES_PER_PAGE)))]


def open_image(img):
    im = Image.open(img)
    im = im.convert("RGB")
    return im


@timing
def sort_greedy(imagedata):
    """ Sort images by perceptual hash """
    print("Sorting images by perceptual hash")
    im_dict = {i.file_hash: i for i in imagedata}
    total_files = len(imagedata)
    start = choice(list(im_dict.keys()))
    start_im = im_dict[start]
    sorted_data = [im_dict[start]]
    im_dict.pop(start)
    with tqdm(total=total_files) as pbar:
        while im_dict:
            pbar.update(1)
            best_match = None
            best_score = 0
            for fhash, value in (im_dict.items()):
                score = abs(start_im.phash - value.phash)
                if score < best_score or best_match is None:
                    best_match = fhash
                    best_score = score
            sorted_data.append(im_dict[best_match])
            start = best_match
            start_im = im_dict[best_match]
            im_dict.pop(best_match)
    return sorted_data


@timing
def process_all_images(images):
    pool_obj = multiprocessing.Pool()
    return list(tqdm(pool_obj.imap(generaate_image_metadata, images), total=len(images)))


@timing
def generaet_all_thumbs(images):
    Path("docs/thumbnails/").mkdir(parents=True, exist_ok=True)
    pool_obj = multiprocessing.Pool()
    return list(tqdm(pool_obj.imap(generate_thumbnail_if_not_exists, images), total=len(images)))


def index_to_file(index):
    filen = index // NUM_IMAGES_PER_PAGE
    if filen == 0:
        return "index.html"
    return str(filen) + ".html"


def remove_files_with_extension(ext):
    for file in Path("./docs").glob(ext):
        os.remove(file)


if __name__ == "__main__":
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('template.html')

    images = []
    for paths in [Path('docs/images').rglob(ext) for ext in required_extensions]:
        for path in list(paths):
            images.append(path.relative_to('.'))

    print("Generating metadata...")
    imagedata = dedupe(process_all_images(images))
    shuffle(imagedata)

    print("Generating thumbnails...")
    generaet_all_thumbs(imagedata)

    imagedata = sort_greedy(imagedata)

    # dom_cols = generate_dominant_colors(imagedata)

    print("Rendering pages...")
    remove_files_with_extension("*.html")
    max_index = len(imagedata) // NUM_IMAGES_PER_PAGE
    for index, imageset in (enumerate(chunks(imagedata, NUM_IMAGES_PER_PAGE))):
        subs = template.render(title=index, imagedata=imageset,
                               index=index, max_index=max_index)
        output_file = "docs/{}.html".format(index)
        if index == 0:
            output_file = "docs/index.html"
        with open(output_file, 'w') as f:
            f.write(subs)

    thumb = template.render(title="*", imagedata=imagedata,
                            mode="thumb",
                            index_to_file=index_to_file,
                            enumerate=enumerate,
                            index=max_index, max_index=max_index)
    output_file = "docs/thumb.html"
    with open(output_file, 'w') as f:
        f.write(thumb)
    print("Done!")
