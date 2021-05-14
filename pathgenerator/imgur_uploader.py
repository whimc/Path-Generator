import pyimgur
import webbrowser
from threading import Thread, Lock

import pathgenerator.config as config


mutex = Lock()


def auth_with_pin(client):
    """Authorize Imgur client with a PIN

    Arguments:
        client {pyimgur.Client} -- Imgur client

    Returns:
        [tuple] -- (access_token, refresh_token) tuple
    """
    auth_url = client.authorization_url('pin')
    webbrowser.open(auth_url)
    pin = input('What is the pin: ')
    response = client.exchange_pin(pin)

    config.set_multi(config.IMGUR_SECTION,
        ('access_token', response[0]),
        ('refresh_token', response[1])
    )

    return response


def get_authed_client():
    refresh_token = config.get(config.IMGUR_SECTION, 'refresh_token')
    if refresh_token:
        client = pyimgur.Imgur(
            client_id=config.IMGUR_CLIENT_ID,
            client_secret=config.IMGUR_CLIENT_SECRET,
            refresh_token=refresh_token
        )
    else:
        client = pyimgur.Imgur(
            client_id=config.IMGUR_CLIENT_ID,
            client_secret=config.IMGUR_CLIENT_SECRET
        )
        auth_with_pin(client)

    try:
        access_token = client.refresh_access_token()
        config.set(config.IMGUR_SECTION, 'access_token', access_token)
    except Exception as e:
        print(e)
        print('Access token failed to refresh')
        auth_with_pin(client)
        client = pyimgur.Imgur(
            client_id=config.IMGUR_CLIENT_ID,
            client_secret=config.IMGUR_CLIENT_SECRET,
            refresh_token=config.get(config.IMGUR_SECTION, 'refresh_token')
        )

    return client

def upload_image(client, album, img_path, img_name, links, overwrite=False):
    """Uploads a single image to Imgur

    Arguments:
        client {pyimgur.Client} -- Imgur client
        album {pyimgur.Album} -- Imgur album
        img_path {str} -- Path of the image to upload
        img_name {str} -- Name of the image to upload
        links {list(str)} -- List of links of uploaded images

    Keyword Arguments:
        overwrite {bool} -- If an image is found within the album, overwrite it?(default: {False})
    """
    for image in album.images:
        if img_name == image.title:
            if overwrite:
                # print('Overriding pre-existing image!')
                album.remove_images(image)
            else:
                mutex.acquire()
                # print('FOUND %s: %s' % (image.title, image.link))
                links[img_name] = image.link
                mutex.release()
                return

    image = client.upload_image(path=img_path, title=img_name)
    album.add_images(image)

    mutex.acquire()
    # print('UPLOADED %s: %s' % (image.title, image.link))
    links[img_name] = image.link
    mutex.release()


def upload_to_imgur(path_name_dict, overwrite=False):
    """Uploads a bunch of images to Imgur.

    Arguments:
        path_name_dict {dict} -- (image path, image name) tuple dictionary

    Keyword Arguments:
        overwrite {bool} -- If an image with the same name already exists, should it be overwritten? (default: {False})

    Returns:
        [list] -- List of Imgur links to uploaded images
    """

    client = get_authed_client()
    album = client.get_album(config.IMGUR_ALBUM_ID)

    links = dict()
    threads = []
    for img_path, img_name in path_name_dict.items():
        thread = Thread(target=upload_image, args=(client, album, img_path, img_name, links, overwrite))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return links
