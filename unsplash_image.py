from pathlib import Path
from client import HttpClient


def main():
    image_url = f"https://images.unsplash.com/photo-1763688506750-0da09fe27324?q=80&w=1032&auto=format&fit=crop"

    HttpClient().download(image_url, "unsplash_image.jpg")
    print(f"Downloaded Unsplash image")


if __name__ == "__main__":
    main()
