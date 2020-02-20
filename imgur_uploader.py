import pyimgur
import webbrowser
from threading import Thread, Lock

import secrets
from configparser import ConfigParser

mutex = Lock()

def set_config_val(config_parser, key, val):
    """Set a value within the 'imgur' section of the config
    
    Arguments:
        config_parser {configparser.ConfigParser} -- The config parser to set from
        key {str} -- The key of the config entry
        val {str} -- The value of the config entry
    """
    set_config_val_dict(config_parser, {key: val})


def set_config_val_dict(config_parser, arg_dict):
    """Sets a all key/value pairs from a diction in the 'imgur' section of the config
    
    Arguments:
        config_parser {configparser.ConfigParser} -- The config parser to set from
        arg_dict {dict} -- The dictionary containing key/value config entries
    """
    for key, val in arg_dict.items():
        config_parser.set('imgur', key, val)
    with open('config.ini', 'w') as file:
        config_parser.write(file)


def get_config_val(config_parser, key, fallback=None):
    """Get a value from the 'imgur' section of the config
    
    Arguments:
        config_parser {configparser.ConfigParser} -- The config parser to get from
        key {str} -- The key of the config entry
    
    Keyword Arguments:
        fallback {str} -- Default value to return if key is not found/set (default: {None})
    
    Returns:
        [str] -- Value within the config matching 'key'
    """
    return config_parser.get('imgur', key, fallback=fallback)


def get_config_val_dict(config_parser, *args):
    """Get a dictionary of key/value entries from the 'imgur' section of the config
    
    Arguments:
        config_parser {configparser.ConfigParser} -- The config parser to get from
    
    Returns:
        [dict] -- Key/value config entries
    """
    return { key : get_config_val(config_parser, key) for key in args }


def auth_with_pin(client, config_parser):
    """Authorize Imgur client with a PIN
    
    Arguments:
        client {pyimgur.Client} -- Imgur client
        config_parser {configparser.ConfigParser} -- Config parser for getting values
    
    Returns:
        [tuple] -- (access_token, refresh_token) tuple
    """
    auth_url = client.authorization_url('pin')
    webbrowser.open(auth_url)
    pin = input('What is the pin: ')
    response = client.exchange_pin(pin)

    set_config_val_dict(config_parser, {
        'access_token': response[0],
        'refresh_token': response[1],
    })

    return response


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

    parser = ConfigParser()
    parser.read('config.ini')

    if not parser.get('imgur', 'client_id') or not parser.get('imgur', 'client_secret'):
        print('Please enter the `client_id` and `client_secret` into `config.ini`!')
        exit()

    if get_config_val(parser, 'refresh_token'):
        client = pyimgur.Imgur(**get_config_val_dict(parser, 
            'client_id', 'client_secret', 'refresh_token'
        ))
    else:
        client = pyimgur.Imgur(**get_config_val_dict(parser, 
            'client_id', 'client_secret'
        ))
        auth_with_pin(client, parser)

    try:
        access_token = client.refresh_access_token()
        set_config_val(parser, 'access_token', access_token)
    except:
        print('Access token failed to refresh')
        auth_with_pin(client, parser)
        client = pyimgur.Imgur(**get_config_val_dict(parser, 
            'client_id', 'client_secret', 'refresh_token'
        ))

    username = get_config_val(parser, 'username')
    album_id = get_config_val(parser, 'album_id')

    if not username:
        username = input('What is the username?')
        set_config_val(parser, 'username', username)
    if not album_id:
        album_id = input('What is the album id?')
        set_config_val(parser, 'album_id', album_id)

    user = client.get_user(username)
    album = client.get_album(album_id)

    links = dict()
    threads = []
    for img_path, img_name in path_name_dict.items():
        thread = Thread(target=upload_image, args=(client, album, img_path, img_name, links, overwrite))
        threads.append(thread)
        thread.start()        

    for thread in threads:
        thread.join()

    return links
