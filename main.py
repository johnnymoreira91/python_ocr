from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io

app = FastAPI()

def preprocess_image(image: Image.Image) -> Image.Image:
    # Convertendo para escala de cinza
    image = image.convert('L')
    # Aumentando o contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    # Aplicando um filtro de nitidez
    image = image.filter(ImageFilter.SHARPEN)
    return image

def crop_bottom_part(image: Image.Image) -> Image.Image:
    # Pega as dimensões da imagem
    width, height = image.size
    # Define a área para cortar (últimos 20% da altura)
    bottom_part = image.crop((0, height * 0.8, width, height))
    return bottom_part

@app.post("/image")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Carregar a imagem enviada
        image = Image.open(io.BytesIO(await file.read()))

        # Recortar a parte inferior da imagem
        image = crop_bottom_part(image)

        # Pré-processar a imagem
        image = preprocess_image(image)

        # Parâmetros do Tesseract para melhor reconhecimento
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(image, lang='por', config=custom_config)

        if not extracted_text.strip():
            return JSONResponse(content={"error": "No text extracted. Please check the quality of the image or try a different image."}, status_code=400)

        return {"extracted_text": extracted_text}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
