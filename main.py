from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.SHARPEN)
    return image

def crop_bottom_part(image: Image.Image) -> Image.Image:
    width, height = image.size
    bottom_part = image.crop((0, height * 0.8, width, height))
    return bottom_part

def resize_image(image: Image.Image, width: int) -> Image.Image:
    aspect_ratio = image.height / image.width
    new_height = int(width * aspect_ratio)
    return image.resize((width, new_height), Image.LANCZOS)

@app.post("/image")
async def extract_text(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read()))

        image = crop_bottom_part(image)

        image = resize_image(image, 8000)

        image = preprocess_image(image)

        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(image, lang='por', config=custom_config)

        if not extracted_text.strip():
            return JSONResponse(content={"error": "No text extracted. Please check the quality of the image or try a different image."}, status_code=400)

        return {"extracted_text": extracted_text}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
