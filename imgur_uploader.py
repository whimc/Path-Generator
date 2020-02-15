import pyimgur
import webbrowser

import secrets
from configparser import ConfigParser

def auth_with_pin(client):
    auth_url = client.authorization_url('pin')
    webbrowser.open(auth_url)
    pin = input('What is the pin?')
    response = client.exchange_pin(pin)
    print(response)
#   setter.set_authentication(new_access_token = response[0], new_refresh_token = response[1])
    return response


def upload_to_imgur(img_path, img_name, override=False):
    """Uploads an image to Imgur.
    
    Arguments:
        img_path {str} -- Path to an image to upload
        img_name {str} -- Name of the picture once uploaded to Imgur
    
    Keyword Arguments:
        override {bool} -- If an image with the same name already exists, should it be overwritten? (default: {False})
    
    Returns:
        [str] -- Imgur link to uploaded image
    """

    print('\n\nGetting Imgur client...')

    parser = ConfigParser()
    parser.read('config.ini')

    client = pyimgur.Imgur(
        client_id=secrets.IMGUR_CLIENT_ID,
        client_secret=secrets.IMGUR_CLIENT_SECRET,
    )

    if not secrets.IMGUR_CLIENT_ID or not secrets.IMGUR_CLIENT_SECRET:
        print('Please enter the IMGUR_CLIENT_ID and IMGUR_CLIENT_SECRET into `config.ini`!')
        exit()

    if not secrets.IMGUR_REFRESH_TOKEN:
        print('IMGUR_REFRESH_TOKEN does not exist within `secrets.py`')
        auth_with_pin(client)

        client = pyimgur.Imgur(
            client_id=secrets.IMGUR_CLIENT_ID,
            client_secret=secrets.IMGUR_CLIENT_SECRET,
            refresh_token=secrets.IMGUR_REFRESH_TOKEN
        )

    try:
        print('Refreshing access token')
        client.refresh_access_token()
    except:
        print('Access token failed to refresh')
        response = auth_with_pin(client)
        client = pyimgur.Imgur(
            client_id=secrets.IMGUR_CLIENT_ID,
            client_secret=secrets.IMGUR_CLIENT_SECRET,
            refresh_token=secrets.IMGUR_REFRESH_TOKEN
        )

    print('Client retrieved')

    username = secrets.IMGUR_USERNAME
    album_id = secrets.IMGUR_ALBUM_ID

    if not secrets.IMGUR_USERNAME:
        username = input('What is the username?')
        # setter.set_credentials(new_username=username)
    if not secrets.IMGUR_ALBUM_ID:
        album_id = input('What is the album id?')
        # setter.set_credentials(new_album_id=album_id)

    user = client.get_user(username)
    album = client.get_album(album_id)

    for image in album.images:
        if img_name == image.title:
            if override:
                print('Overriding pre-existing image!')
                album.remove_images(image)
            else:
                print('Pre-existing image found!')
                print('%s: %s' % (image.title, image.link))
                return image.link
                exit()

    print('Uploading image...')
    image = client.upload_image(path=img_path, title=img_name)
    album.add_images(image)
    print('Image uploaded!')
    print('%s: %s' % (image.title, image.link))

    return image.link
