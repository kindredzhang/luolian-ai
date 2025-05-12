import os
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse

from chat import chat_with_image
from utils import convert_pdf_to_png

app = FastAPI(title="PDF to CSV Converter", description="Convert PDF files to CSV files")

PROJECT_ROOT = os.getcwd()
PDF_DIR = os.path.join(PROJECT_ROOT, "pdf")
PNG_DIR = os.path.join(PROJECT_ROOT, "png")
RESULT_DIR = os.path.join(PROJECT_ROOT, "result")

if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)
if not os.path.exists(PNG_DIR):
    os.makedirs(PNG_DIR)
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

@app.post("/convert-pdf")
async def convert_pdf(file: UploadFile):
    """
    接收PDF文件并转换为PNG
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")

    unique_id = str(uuid.uuid4())
    pdf_path = os.path.join(PDF_DIR, f"{unique_id}.pdf")
    png_path = os.path.join(PNG_DIR, f"{unique_id}.png")

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_path = convert_pdf_to_png(str(pdf_path), str(png_path))
        if not output_path:
            raise HTTPException(status_code=500, detail="PDF转换失败")

        csv_str = chat_with_image(png_path)
        excel_path = os.path.join(RESULT_DIR, f"{Path(file.filename).stem}.csv")
        with open(excel_path, "w") as f:
            f.write(csv_str)
        print(f"已生成 {excel_path}")

        return FileResponse(
            path=excel_path,
            filename=f"{unique_id}.csv",
            media_type="text/csv"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(png_path):
            os.remove(png_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8864) 