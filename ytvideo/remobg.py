from rembg import remove
from PIL import Image
import io

# Load your image
input_path = '/Users/uday/Downloads/images (1).jpeg'  # Replace with your input image path
output_path = 'output_image.png'  # Output path with background removed

with open(input_path, 'rb') as i:
    input_data = i.read()

# Remove background
output_data = remove(input_data)

# Save the output image
with open(output_path, 'wb') as o:
    o.write(output_data)

print("Background removed and saved to", output_path)
