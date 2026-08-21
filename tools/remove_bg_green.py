from PIL import Image

def remove_green():
    try:
        img_path = r"C:\Users\Administrator\.gemini\antigravity-ide\brain\46ab4c77-39c8-41e1-b6ea-c2fa6891f3f9\hero_model_green_1786616441049.png"
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            r, g, b, a = item
            # Chroma key detection: if green is significantly higher than red and blue
            if g > 150 and r < g - 40 and b < g - 40:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
                
        img.putdata(newData)
        img.save('webapp/static/hero_model_transparent.png', "PNG")
        print("Successfully removed green screen!")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    remove_green()
