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

for filename in os.listdir(input_dir):
    if filename.lower().endswith(supported_extensions):
        name, ext = os.path.splitext(filename)
        base_name = name.replace("@3x", "")
        img_path = os.path.join(input_dir, filename)
        img = Image.open(img_path).convert("RGB")

        ios_ratio = ios_base_width / img.width
        ios_base_height = int(img.height * ios_ratio)
        ios_base_img = img.resize((ios_base_width, ios_base_height), Image.LANCZOS)

        for suffix, factor in ios_scales.items():
            size = (int(ios_base_img.width * factor), int(ios_base_img.height * factor))
            resized = ios_base_img.resize(size, Image.LANCZOS)
            output_path = os.path.join(ios_dir, f"{base_name}{suffix}.jpg")
            resized.save(
                output_path,
                format="JPEG",
                quality=90,
                optimize=True,
                icc_profile=icc_profile
            )

        # Android export pipeline
        android_ratio = android_base_width / img.width
        android_base_height = int(img.height * android_ratio)
        android_base_img = img.resize((android_base_width, android_base_height), Image.LANCZOS)

        for dpi, factor in android_scales.items():
            size = (int(android_base_img.width * factor), int(android_base_img.height * factor))
            resized = android_base_img.resize(size, Image.LANCZOS)
            output_path = os.path.join(android_dirs[dpi], f"{base_name}.webp")
            resized.save(
                output_path,
                format="WEBP",
                quality=95,
                method=6,
                icc_profile=icc_profile
            )

print("✅ Export complete.")
