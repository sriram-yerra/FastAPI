from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

# imagekit = ImageKit(
#     {
#         "private_key": os.getenv("IMAGEKIT_PRIVATE_KEY"),
#         # "url_endpoint": os.getenv("IMAGEKIT_URL"),
#     }
# )

imagekit = ImageKit()
'''
Use will upload the file to the API.
Our API will send that Images to the Imagekitio.
Then we will grab that url, save that in our database, and then serve it to the frontend to the user..!
'''
'''
We can do the image transformation within the url only once we 
fetched from the database using imagekitio..!
'''