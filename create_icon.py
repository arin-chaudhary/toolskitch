from PIL import Image
import os

def create_ico_from_png():
    try:
        png_path = "logo.png"
        ico_path = "logo.ico"
        
        if os.path.exists(png_path):
            img = Image.open(png_path)
            
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save(ico_path, format='ICO', sizes=sizes)
            
            print(f"✅ Successfully created {ico_path} from {png_path}")
            print("You can now use logo.ico as your application icon")
        else:
            print("❌ logo.png not found in current directory")
    except ImportError:
        print("❌ PIL/Pillow not installed. Install with: pip install Pillow")
    except Exception as e:
        print(f"❌ Error creating ICO file: {e}")

if __name__ == "__main__":
    create_ico_from_png() 