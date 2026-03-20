import os
import random
import shutil

# Path to your source image folder and target directory where room folders will be created
source_image_folder = "hotel_images"
target_root_folder = "static/rooms"

# Get list of all image files
image_files = [f for f in os.listdir(source_image_folder) if os.path.isfile(os.path.join(source_image_folder, f))]

# Create room folders (10 floors, 10 rooms each: 001, 002, ..., 910)
for floor in range(10):
    for room in range(1, 11):
        room_number = f"{floor}{room:02d}"  # Format: 001, 002, ..., 910
        room_folder_path = os.path.join(target_root_folder, room_number)
        os.makedirs(room_folder_path, exist_ok=True)

        # Randomly choose 3 images (with replacement)
        selected_images = random.choices(image_files, k=3)

        # Copy selected images to room folder
        for idx, img in enumerate(selected_images):
            src = os.path.join(source_image_folder, img)
            dst = os.path.join(room_folder_path, f"img_{idx+1}_{img}")
            shutil.copy(src, dst)

print("✅ All room folders created and populated with images.")
