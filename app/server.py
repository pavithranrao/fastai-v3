import asyncio
import base64
import io
import sys
from pathlib import Path

import aiohttp
import cv2
import numpy as np
import uvicorn
from PIL import Image
from fastai.vision import load_learner, open_image
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_url = 'https://drive.google.com/uc?export=download&id=1vZ-p8eGcRakodbDPbNXB7KL4E4PH26NQ'
export_file_name = 'mnist_model.pkl'

classes = [str(i) for i in range(0, 10)]
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists():
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai " \
                      "and will not work in a CPU environment." \
                      "\n\nPlease update the fastai library in your training environment " \
                      "and export your model again.\n\nSee instructions for 'Returning to work'" \
                      " at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


def string_to_gray(base64_string):
    imgdata = base64.b64decode(str(base64_string))
    image = Image.open(io.BytesIO(imgdata))
    gray_img = Image.fromarray(cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2RGB))

    return gray_img.resize((28, 28))


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = img_data['javascript_data']
    img = string_to_gray(img_bytes)
    img.save("test.png")

    img = open_image("test.png")
    pred_class, _, _ = learn.predict(img)

    return JSONResponse({'result': pred_class.obj})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
