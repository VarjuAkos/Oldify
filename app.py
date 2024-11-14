import cv2
import numpy as np

def load_and_resize_image(file_path, max_size=1000):
    """Load an image and resize it to have a maximum dimension of max_size."""
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {file_path}")
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return img

def convert_to_black_and_white(image):
    """Convert the image to black and white."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_sepia(image):
    """Apply a sepia filter to the image."""
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    return cv2.transform(image, sepia_filter)

def adjust_contrast_brightness(image, contrast_factor=0.2, brightness_factor=5):
    """Adjust the contrast and brightness of the image."""
    return cv2.addWeighted(image, contrast_factor, image, 0, brightness_factor)

def add_noise(image, intensity=0.5):
    """Add noise to the image to simulate film grain."""
    noise = np.random.normal(0, intensity, image.shape).astype(np.uint8)
    return cv2.add(image, noise)

def apply_vignette(image, strength=0.75):
    """Apply a vignette effect to the image."""
    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype=np.float32)
    center = (width // 2, height // 2)
    max_radius = min(center[0], center[1])
    cv2.circle(mask, center, max_radius, (1.0), -1)
    mask = cv2.GaussianBlur(mask, (0, 0), max_radius // 3)
    mask = np.power(mask, strength)
    mask = np.expand_dims(mask, axis=2) if len(image.shape) > 2 else mask
    return (image * mask).astype(np.uint8)


def add_color_fading(image):
    """Simulate slight color fading."""
    faded = cv2.convertScaleAbs(image, alpha=0.9, beta=10)
    return cv2.addWeighted(image, 0.7, faded, 0.3, 0)

def add_subtle_imperfections(image):
    """Add subtle imperfections like small scratches or dust."""
    imperfections = np.zeros(image.shape, dtype=np.uint8)
    for _ in range(50):
        x = np.random.randint(0, image.shape[1])
        y = np.random.randint(0, image.shape[0])
        size = np.random.randint(1, 3)
        color = np.random.randint(200, 256)
        cv2.circle(imperfections, (x, y), size, (color, color, color), -1)
    return cv2.addWeighted(image, 1, imperfections, 0.2, 0)

def load_texture(file_path, target_size):
    """Load and prepare a texture image."""
    texture = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    texture = cv2.resize(texture, target_size, interpolation=cv2.INTER_AREA)
    return texture

def apply_texture(image, texture, blend_mode='overlay', intensity=0.5):
    """Apply a texture to the image using the specified blend mode."""
    # Ensure texture has the same number of channels as the image
    if len(image.shape) == 3 and image.shape[2] == 3:
        texture = cv2.cvtColor(texture, cv2.COLOR_GRAY2BGR)
    
    # Ensure both images have the same data type
    image = image.astype(np.float32)
    texture = texture.astype(np.float32)
    
    if blend_mode == 'overlay':
        # Overlay blend mode
        low = 2 * image * texture / 255.0
        high = 255.0 - 2 * (255.0 - image) * (255.0 - texture) / 255.0
        blended = np.where(image < 128, low, high)
    # Apply the blending with intensity
    result = image * (1 - intensity) + blended * intensity
    
    return np.clip(result, 0, 255).astype(np.uint8)

def process_image(input_path, output_path, apply_sepia_filter=False, max_size=1000):
    """Main function to process the image with vintage effects."""
    # Load and resize the image
    img = load_and_resize_image(input_path, max_size)
    
    # Convert to black and white
    img = convert_to_black_and_white(img)
    
    # Convert back to BGR for color effects
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    # Apply sepia if requested
    if apply_sepia_filter:
        img = apply_sepia(img)
    
    # Apply vintage effects
    img = add_color_fading(img)
    img = add_subtle_imperfections(img)
    img = apply_vignette(img)
        
    # Load and apply textures
    folds_texture = load_texture('images/folds.jpg', (img.shape[1], img.shape[0]))
    oldpaper_texture = load_texture('images/oldpaper.jpg', (img.shape[1], img.shape[0]))
    
    img = apply_texture(img, folds_texture, blend_mode='overlay', intensity=0.5)
    img = apply_texture(img, oldpaper_texture, blend_mode='overlay', intensity=1)
        
    # Save the output image
    cv2.imwrite(output_path, img)
    print(f"Processed image saved to {output_path}")

if __name__ == "__main__":
    # Use forward slashes for cross-platform compatibility
    input_image = "./images/IMG_8348.jpeg"
    output_image = "./images/output_IMG_8348.jpeg"
    process_image(input_image, output_image, apply_sepia_filter=True, max_size=1000)
