import os
import requests
from PIL import Image
from pathlib import Path
from io import BytesIO

class ImageResizer:
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    def __init__(self, output_folder="resized_images"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def process_from_url(self, url, width=None, height=None, scale=None, 
                        maintain_aspect=True, output_format=None, quality=95,
                        filename=None):
        try:
            print(f"Downloading from: {url}")
            
            # Download image
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Open image from downloaded content
            img = Image.open(BytesIO(response.content))
            
            print(f"Original size: {img.size[0]}x{img.size[1]}")
            
            # Calculate new dimensions
            new_size = self._calculate_size(img.size, width, height, 
                                           scale, maintain_aspect)
            
            print(f"New size: {new_size[0]}x{new_size[1]}")
            
            # Resize image
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Determine output filename
            if not filename:
                filename = Path(url).name or "downloaded_image"
                if not any(filename.lower().endswith(ext) for ext in self.SUPPORTED_FORMATS):
                    filename += ".jpg"
            
            # Apply output format if specified
            if output_format:
                filename = Path(filename).stem + f".{output_format.lower()}"
            
            output_path = self.output_folder / filename
            
            # Save with appropriate settings
            save_kwargs = {'quality': quality, 'optimize': True}
            
            if output_format and output_format.lower() == 'png':
                save_kwargs = {'optimize': True}
            elif resized.mode == 'RGBA' and output_format and output_format.lower() in ['jpg', 'jpeg']:
                # Convert RGBA to RGB for JPEG
                rgb = Image.new('RGB', resized.size, (255, 255, 255))
                rgb.paste(resized, mask=resized.split()[3])
                resized = rgb
            
            resized.save(output_path, **save_kwargs)
            print(f"✓ Saved to: {output_path}\n")
            return output_path
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to download image: {e}\n")
            return None
        except Exception as e:
            print(f"✗ Failed to process image: {e}\n")
            return None
    
    def process_from_urls(self, urls, **kwargs):
        print(f"Processing {len(urls)} images...\n")
        successful = 0
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}]")
            if self.process_from_url(url, **kwargs):
                successful += 1
        
        print(f"Completed! {successful}/{len(urls)} images processed")
        print(f"Output folder: {self.output_folder}")
    
    def process_from_folder(self, input_folder, **kwargs):
        input_folder = Path(input_folder)
        images = self._get_images(input_folder)
        
        if not images:
            print(f"No images found in {input_folder}")
            return
        
        print(f"Found {len(images)} images to process\n")
        processed = 0
        
        for img_path in images:
            try:
                with Image.open(img_path) as img:
                    print(f"Processing: {img_path.name}")
                    print(f"Original size: {img.size[0]}x{img.size[1]}")
                    
                    new_size = self._calculate_size(img.size, kwargs.get('width'), 
                                                    kwargs.get('height'), 
                                                    kwargs.get('scale'), 
                                                    kwargs.get('maintain_aspect', True))
                    
                    print(f"New size: {new_size[0]}x{new_size[1]}")
                    
                    resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    output_format = kwargs.get('output_format')
                    if output_format:
                        filename = img_path.stem + f".{output_format.lower()}"
                    else:
                        filename = img_path.name
                    
                    output_path = self.output_folder / filename
                    
                    save_kwargs = {'quality': kwargs.get('quality', 95), 'optimize': True}
                    
                    if output_format and output_format.lower() == 'png':
                        save_kwargs = {'optimize': True}
                    elif resized.mode == 'RGBA' and output_format and output_format.lower() in ['jpg', 'jpeg']:
                        rgb = Image.new('RGB', resized.size, (255, 255, 255))
                        rgb.paste(resized, mask=resized.split()[3])
                        resized = rgb
                    
                    resized.save(output_path, **save_kwargs)
                    processed += 1
                    print(f"✓ Saved to: {output_path}\n")
                    
            except Exception as e:
                print(f"✗ Failed to process {img_path.name}: {e}\n")
        
        print(f"Completed! {processed}/{len(images)} images processed")
        print(f"Output folder: {self.output_folder}")
    
    def _get_images(self, folder):
        images = []
        for ext in self.SUPPORTED_FORMATS:
            images.extend(folder.glob(f"*{ext}"))
            images.extend(folder.glob(f"*{ext.upper()}"))
        return sorted(images)
    
    def _calculate_size(self, original_size, width, height, scale, maintain_aspect):
        orig_w, orig_h = original_size
        
        if scale:
            return (int(orig_w * scale), int(orig_h * scale))
        
        if width and height:
            if maintain_aspect:
                ratio = min(width / orig_w, height / orig_h)
                return (int(orig_w * ratio), int(orig_h * ratio))
            else:
                return (width, height)
        
        if width:
            ratio = width / orig_w
            return (width, int(orig_h * ratio))
        
        if height:
            ratio = height / orig_h
            return (int(orig_w * ratio), height)
        
        return original_size
def main():
    resizer = ImageResizer(output_folder="resized_images")
    print("=== Processing Single URL ===\n")
    image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2JFyVMUGB2hCmAhFXOdCydqzgsCHd2BAzEA&s"  # REPLACE WITH YOUR IMAGE URL
    resizer.process_from_url(
        url=image_url,
        width=800,  
        output_format='jpg',
        quality=90
    )
if __name__ == "__main__":
    main()