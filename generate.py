from concurrent.futures import process
from random import shuffle
import underscore_image
import jinja2
from pathlib import Path
import hashlib
from PIL import Image
import imagehash
from dataclasses import dataclass, field
import multiprocessing
from tqdm import tqdm
import os
required_extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]
NUM_IMAGES_PER_PAGE = 99
ignored_files = []
with open("ignore.txt", "r") as f:
    ignored_files = f.read().splitlines()


@dataclass(order=True)
class UnderscoreImage:
    """ Image class """
    path: str
    fhash: str
    phash: str


def open_image_pil(img):
    im = Image.open(img)
    im = im.convert("RGB")
    return im


def generate_hash(img) -> str:
    """Generate a hash of the file"""
    return hashlib.md5(img).hexdigest()
    if fhash in ignored_files:
        return None


def generate_metadata(image_path):
    with open(image_path, 'rb') as imagefile:
        img = imagefile.read()
        fhash = generate_hash(img)
        phash = str(imagehash.colorhash(
            open_image_pil(image_path), binbits=32))
        return UnderscoreImage(image_path, fhash, phash)


def parallel_process_images(images):
    pool_obj = multiprocessing.Pool()
    return list(tqdm(pool_obj.imap(generate_metadata, images), total=len(images)))


def dedupe(imagedata):
    deduped_list = []
    seen_hashes = set()
    for image in imagedata:
        if image is not None:
            if image.fhash not in seen_hashes:
                seen_hashes.add(image.fhash)
                deduped_list.append(image)
    return deduped_list


def remove_files_with_extension(ext):
    for file in Path("./docs").glob(ext):
        os.remove(file)


def chunks(lst, n_chunks):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n_chunks):
        yield lst[i:i + n_chunks]


if __name__ == "__main__":
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('template.html')

    image_paths = []
    for paths in [Path('docs/images').rglob(ext) for ext in required_extensions]:
        for path in list(paths):
            image_paths.append(path.relative_to('.'))
    # image_paths = image_paths[:500]
    underscore_image.maybe_create_table()

    images_to_be_processed = []
    for image_path in image_paths:
        if not underscore_image.does_image_exist(image_path):
            images_to_be_processed.append(image_path)

    processed_images = parallel_process_images(images_to_be_processed)

    for processed_image in processed_images:
        underscore_image.insert_image((processed_image.fhash,
                                       processed_image.path, processed_image.phash))

    imagedata = [UnderscoreImage(path, fhash, phash) for (
        fhash, path, phash) in underscore_image.fetch_all_images()]

    remove_files_with_extension("*.html")

    shuffle(imagedata)

    max_index = len(imagedata) // NUM_IMAGES_PER_PAGE
    for index, imageset in (enumerate(chunks(imagedata, NUM_IMAGES_PER_PAGE))):
        subs = template.render(title=index, imagedata=imageset,
                               index=index, max_index=max_index)
        output_file = "docs/{}.html".format(index)
        if index == 0:
            output_file = "docs/index.html"
        with open(output_file, 'w') as f:
            f.write(subs)

    print("Done!")
