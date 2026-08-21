from PIL import Image

def clean_and_crop():
    try:
        # Open original green screen image
        img_path = r"C:\Users\Administrator\.gemini\antigravity-ide\brain\46ab4c77-39c8-41e1-b6ea-c2fa6891f3f9\hero_model_green_1786616441049.png"
        img = Image.open(img_path).convert("RGBA")
        width, height = img.size
        datas = img.getdata()
        
        newData = []
        min_y = height
        max_y = 0
        min_x = width
        max_x = 0
        
        # We'll use a stricter chroma key to remove green fringes
        for y in range(height):
            for x in range(width):
                r, g, b, a = datas[y * width + x]
                # Stricter green detection
                if g > 100 and g > r * 1.2 and g > b * 1.2:
                    newData.append((255, 255, 255, 0))
                else:
                    # Not green, keep it, and update bounding box
                    newData.append((r, g, b, a))
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
                    
        img.putdata(newData)
        
        # Crop the image to the bounding box so the person touches the bottom!
        # We can add a little padding to the top if we want, but bottom must be exactly max_y
        cropped_img = img.crop((min_x, min_y, max_x + 1, max_y + 1))
        cropped_img.save('webapp/static/hero_model_transparent.png', "PNG")
        print(f"Successfully cleaned and cropped from {width}x{height} to bounding box ({min_x}, {min_y}) - ({max_x}, {max_y})!")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    clean_and_crop()
