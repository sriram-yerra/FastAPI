from fastapi import FastAPI
import requests, time, os
import httpx, asyncio

app = FastAPI()

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

'''
For each iteration:
    Send request to image URL
    Server waits for full image to download
    Only after completion → next image starts
- No parallelism
- Total time = sum of all image download times
'''
'''
Response body
{
  "method": "blocking",
  "duration": 15.35,
  "message": "Downloaded all 10 Imges"
}
'''
@app.get("/blocking")
def download_images_blocking():
    start = time.time()

    response = requests.get("https://picsum.photos/v2/list?limit=10")
    response.raise_for_status()
    images = response.json()

    for i,img in enumerate(images):
        img_url = img['download_url']
        img_data = requests.get(img_url).content

        with open(f"{IMAGES_DIR}/blocking_img{i}.jpg", "wb") as f:
            f.write(img_data)

    end = time.time()

    return {
        "method": "blocking",
        "duration": round(end - start, 2),
        "message": "Downloaded all 10 Imges"
    }

'''
What is Generator?
A generator is a special function that returns values one by one instead of returning everything at once.
It used Yield insted of return statememt
'''
@app.get("/non-blocking")
async def download_images_NonBlocking():
    start = time.time()

    timeout = httpx.Timeout(30.0, connect=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get("https://picsum.photos/v2/list?limit=10")
        response.raise_for_status()
        images = response.json()

        async def download_images(img, i):
            try:
                img_url = img['download_url']

                img_response = await client.get(img_url, follow_redirects=True)
                img_response.raise_for_status()

                with open(f"{IMAGES_DIR}/non_blocking_img{i}.jpg", "wb") as f:
                    f.write(img_response.content)

            except httpx.ReadTimeout:
                print("Timeout While Downloading Images..!")

        await asyncio.gather(*(download_images(img, i) for i, img in enumerate(images)))

    end = time.time()

    return {
        "method": "non-blocking",
        "duration": round(end - start, 2),
        "message": "Downloaded all 10 Imges"
    }