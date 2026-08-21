from PIL import Image

def remove_bg():
    try:
        img = Image.open('webapp/static/hero_model.png').convert("RGBA")
        datas = img.getdata()
        
        # Get background color from top-left pixel
        bg_color = datas[0]
        # We will allow some tolerance
        tolerance = 40
        
        newData = []
        for item in datas:
            # Check if pixel is close to bg_color
            if abs(item[0] - bg_color[0]) < tolerance and \
               abs(item[1] - bg_color[1]) < tolerance and \
               abs(item[2] - bg_color[2]) < tolerance:
                # Replace with transparent
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
                
        img.putdata(newData)
        img.save('webapp/static/hero_model_transparent.png', "PNG")
        print("Successfully removed background!")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    remove_bg()
