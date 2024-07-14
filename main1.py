from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import uvicorn
import io

app = FastAPI()

# Configuração para permitir requisições de qualquer origem (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir requisições de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP
    allow_headers=["*"],  # Permitir todos os headers HTTP
)

# Se necessário, especifique o caminho do executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def ocr_from_image(image_path):
    # Carregue a imagem
    image = Image.open(image_path)
    
    # Use pytesseract para extrair o texto
    text = pytesseract.image_to_string(image, lang='por')  # Idioma: português
    
    return text

@app.post("/image")
async def upload_image(image: UploadFile = File(...)):
    try:
        with open(image.filename, "wb") as buffer:
            buffer.write(image.file.read())

        # Realiza OCR na imagem e obtém o texto extraído
        extracted_text = ocr_from_image(image.filename)

        # Retorna o texto extraído como JSON
        return JSONResponse(content={"extracted_text": extracted_text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/upload")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Carregar a imagem enviada
        image = Image.open(io.BytesIO(await file.read()))

        # Parâmetros do Tesseract para melhor reconhecimento
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(image, lang='por', config=custom_config)

        if not extracted_text.strip():
            return JSONResponse(content={"error": "No text extracted. Please check the quality of the image or try a different image."}, status_code=400)

        return {"extracted_text": extracted_text}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
