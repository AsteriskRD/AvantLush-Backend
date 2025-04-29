import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from pathlib import Path

# Your Cloudinary configuration is already set in settings.py,
# but let's include it here for completeness
cloudinary.config( 
    cloud_name = 'dvfwa8fzh',
    api_key = '345125992849241', 
    api_secret = '2ZGsMf9ofeLgqpWdgYHRzK1QWM8'
)

def upload_image(image_path, folder="email_templates"):
    """
    Upload an image to Cloudinary and return the URL.
    
    Args:
        image_path (str): Local path to the image file
        folder (str): Optional folder name in Cloudinary
        
    Returns:
        str: URL of the uploaded image
    """
    try:
        # Make sure the file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Upload the image
        upload_result = cloudinary.uploader.upload(
            image_path,
            folder=folder,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
        
        # Get the URL (secure_url is HTTPS)
        image_url = upload_result['secure_url']
        
        print(f"Image uploaded successfully. URL: {image_url}")
        return image_url
    
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Path to your image
    image_path = r"C:\Users\ADMIN\Downloads\AvantLush-Backend\avantlush_backend\api\templates\AvantLush Brand Secondary Logo Green 1.png"
    
        # Upload the image and get the URL
    image_url = upload_image(image_path)
    
    if image_url:
        print("You can use this URL in your email templates:")
        print(image_url)
    else:
        print("Failed to upload image.")