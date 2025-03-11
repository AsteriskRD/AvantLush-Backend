const cloudinary = require('cloudinary').v2;
const fs = require('fs');
const path = require('path');

// Configure Cloudinary
cloudinary.config({
  cloud_name: 'dvfwa8fzh',
  api_key: '345125992849241',
  api_secret: '2ZGsMf9ofeLgqpWdgYHRzK1QWM8'
});

// Function to upload a single image
async function uploadImage(imagePath) {
  try {
    const result = await cloudinary.uploader.upload(imagePath, {
      folder: 'products',
      use_filename: true,
      unique_filename: true
    });
    return result.secure_url;
  } catch (error) {
    console.error(`Error uploading ${imagePath}:`, error);
    return null;
  }
}

// Function to process multiple product images
async function uploadProductImages(imageFolder) {
  const imageFiles = fs.readdirSync(imageFolder);
  const uploadedImages = {};

  for (const file of imageFiles) {
    if (file.match(/\.(jpg|jpeg|png|gif)$/i)) {
      const fullPath = path.join(imageFolder, file);
      const url = await uploadImage(fullPath);
      if (url) {
        uploadedImages[file] = url;
        console.log(`Uploaded: ${file} -> ${url}`);
      }
    }
  }

  return uploadedImages;
}

// Main function
async function main() {
  try {
    const uploadResults = await uploadProductImages('./images');
    console.log('All images uploaded:', uploadResults);
    
    // Optional: You could write these URLs to a file for reference
    fs.writeFileSync('uploaded_images.json', JSON.stringify(uploadResults, null, 2));
  } catch (error) {
    console.error('Error in upload process:', error);
  }
}

main();