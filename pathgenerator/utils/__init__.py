from PIL import Image

def scale(val, src, dst):
    """Scale the given value from the scale of src to the scale of dst"""
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

def resized_copy(image: Image.Image, width) -> Image.Image:
    """Resize a Pillow Image to the given width while maintaining the aspect ratio"""
    wpercent = width / image.size[0]
    hsize = int(image.size[1] * wpercent)
    return image.resize((width, hsize), Image.Resampling.LANCZOS)
