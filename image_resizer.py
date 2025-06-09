from PIL import Image
import os

input_dir = "master"
ios_dir = "ios"
android_dirs = {
    "mdpi": "android/drawables-mdpi",
    "hdpi": "android/drawables-hdpi",
    "xhdpi": "android/drawables-xhdpi",
    "xxhdpi": "android/drawables-xxhdpi",
    "xxxhdpi": "android/drawables-xxxhdpi",
}

os.makedirs(ios_dir, exist_ok=True)
for path in android_dirs.values():
    os.makedirs(path, exist_ok=True)

ios_base_width = 1920
android_base_width = 2400

ios_scales = {
    "@3x": 1.0,
    "@2x": 2 / 3,
    "": 1 / 3  
}

android_scales = {
    "xxxhdpi": 1.0,
    "xxhdpi": 4 / 6,
    "xhdpi": 3 / 6,
    "hdpi": 2 / 6,
    "mdpi": 1 / 6
}

supported_extensions = (".jpg", ".jpeg", ".png")

icc_profile = None
icc_path = "sRGB_IEC61966-2-1_black_scaled.icc"
if os.path.exists(icc_path):
    with open(icc_path, "rb") as f:
        icc_profile = f.read()
else:
    print("ICC profile not found. Skiping color management.")

def crop_to_16_9(image: Image.Image) -> Image.Image:
    w, h = image.size
    target_ratio = 16 / 9
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = round(h * target_ratio)
        left = (w - new_w) // 2
        return image.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = round(w / target_ratio)
        top = (h - new_h) // 2
        return image.crop((0, top, w, top + new_h))
    return image

for filename in os.listdir(input_dir):
    if filename.lower().endswith(supported_extensions):
        name, ext = os.path.splitext(filename)
        base_name = name.replace("@3x", "")
        path = os.path.join(input_dir, filename)
        img = Image.open(path).convert("RGB")

        # Crop to 16:9
        img = crop_to_16_9(img)

        # iOS resize
        ios_ratio = ios_base_width / img.width
        ios_height = int(img.height * ios_ratio)
        ios_base = img.resize((ios_base_width, ios_height), Image.LANCZOS)

        for suffix, factor in ios_scales.items():
            size = (int(ios_base.width * factor), int(ios_base.height * factor))
            resized = ios_base.resize(size, Image.LANCZOS)
            out_path = os.path.join(ios_dir, f"{base_name}{suffix}.jpg")
            resized.save(out_path, format="JPEG", quality=100, optimize=True, icc_profile=icc_profile)

        # Android resize
        android_ratio = android_base_width / img.width
        android_height = int(img.height * android_ratio)
        android_base = img.resize((android_base_width, android_height), Image.LANCZOS)

        for dpi, factor in android_scales.items():
            size = (int(android_base.width * factor), int(android_base.height * factor))
            resized = android_base.resize(size, Image.LANCZOS)
            out_path = os.path.join(android_dirs[dpi], f"{base_name}.webp")
            resized.save(out_path, format="WEBP", quality=100, method=6, icc_profile=icc_profile)

print("✅ Export complete.")
