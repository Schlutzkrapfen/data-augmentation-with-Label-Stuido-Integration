import os
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ImageTransformer:
    """Base class that holds shared parameters for all image transformations."""

    def __init__(self, image_paths, path_to_label, output_path):

        self.image_paths = image_paths
        self.path_to_label = path_to_label
        self.output_path = output_path

    # --- Label helpers ---

    @staticmethod
    def get_picture_label(path_to_labels, id):
        with open(path_to_labels, "r") as f:
            data = json.load(f)
        return data[id]

    def change_path_label(self,data, filepath):
        old_path = data["data"]["image"]
        old_dir = os.path.dirname(old_path)
        if self.output_path:
            old_dir = self.output_path
        file = os.path.join(old_dir, os.path.basename(filepath))
        data["data"]["image"] = file
        return data

    @staticmethod
    def change_mirror_path(data):
        """Mirrors the labels."""
        for annotation in data['annotations']:
            for item in annotation['result']:
                if item['type'] != 'rectanglelabels':
                    continue
                x = item['value']['x']
                width = item['value']['width']
                item['value']['x'] = 100 - x - width
        return data

    def add_labels(self,path_to_labels, id, file_name):
        copied_result = ImageTransformer.get_picture_label(path_to_labels, id)
        changed_result = self.change_path_label(copied_result, file_name)
        with open(path_to_labels, 'r') as f:
            data = json.load(f)
        data.append(changed_result)
        with open(path_to_labels, 'w') as f:
            json.dump(data, f, indent=4)
        print("   added the task to the json")

    def change_mirror_labels(self,path_to_labels, id, file_name):
        copied_result = ImageTransformer.get_picture_label(path_to_labels, id)
        changed_result = self.change_path_label(copied_result, file_name)
        changed_result = ImageTransformer.change_mirror_path(changed_result)
        with open(path_to_labels, 'r') as f:
            data = json.load(f)
        data.append(changed_result)
        with open(path_to_labels, 'w') as f:
            json.dump(data, f, indent=4)
        print("   added the task to the json")

    # --- Core transform engine ---

    def _apply_transform(self, suffix, transform_fn, label_fn=None):
        """Base helper: open each image, apply transform_fn, save, and label."""
        if label_fn is None:
            label_fn = self.add_labels 

        saved_paths = []
        for i, filepath in enumerate(self.image_paths):
            name, ext = os.path.splitext(filepath)
            new_filepath = f"{name}-{suffix}{ext}"
            with Image.open(filepath) as img:
                result = transform_fn(img)
                result.save(new_filepath)
            saved_paths.append(new_filepath)
            print(f"  Saved: {os.path.basename(new_filepath)}")
            label_fn(self.path_to_label, i, new_filepath)
        return saved_paths

    # --- Public transforms ---

    def adjust_brightness(self, factor=1.5):
        """Adjust the brightness of the image."""
        return self._apply_transform(
            suffix=f"brit-{factor}",
            transform_fn=lambda img: ImageEnhance.Brightness(img).enhance(factor)
        )

    def add_gaussian_filter(self, strength=1):
        """Adds a Gaussian filter to the image."""
        return self._apply_transform(
            suffix=f"gaus-{strength}",
            transform_fn=lambda img: img.filter(ImageFilter.GaussianBlur(radius=strength))
        )

    def mirror(self):
        """Mirrors the image."""
        return self._apply_transform(
            suffix="mirrored",
            transform_fn=ImageOps.mirror,
            label_fn=self.change_mirror_labels
        )