import pillow_avif
import pillow_heif
import os
from PIL import Image, UnidentifiedImageError
from shutil import move

def convert_avif_to_pngs(src_dir, dst_dir):
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            png_fp = file_path.replace("avif", "png")
            png_name = file.replace("avif", "png")
            if ".avif" not in file_path or png_name in files:
                print(f"Skipping {file_path} because already converted")
                continue

            try:
                print(f"Converting {file_path}")
                img = Image.open(file_path)
                target_path = os.path.join(dst_dir, png_name)
                img.save(target_path)
            except UnidentifiedImageError:
                breakpoint()
    
def organize_folders(src_dir):
    current_filename = False
    images = []
    for root, _, files in os.walk(src_dir):
        images.extend(files)
        break

    for image in images:
        abs_name = ''.join([i for i in image.replace(".mp4", "") if not i.isdigit()])
        if not current_filename or image.find(abs_name) == -1:
            current_filename = abs_name

        file_path = os.path.join(root, image)
        print(f"Processing {file_path}")

        folder_path = os.path.join(root, abs_name)

        if not os.path.exists(folder_path):
            print(f"Creating folder {folder_path}")
            os.mkdir(folder_path)

        print(f"Moving file {file_path} to {folder_path}")
        move(file_path, folder_path)