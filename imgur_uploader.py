import pyimgur
import webbrowser

import secrets
from configparser import ConfigParser

def set_config_val(config_parser, key, val):
    set_config_val_dict(config_parser, {key: val})

def set_config_val_dict(config_parser, arg_dict):
    for key, val in arg_dict.items():
        config_parser.set('imgur', key, val)
    with open('config.ini', 'w') as file:
        config_parser.write(file)

def get_config_val(config_parser, key, fallback=None):
    return config_parser.get('imgur', key, fallback=fallback)

def get_config_val_dict(config_parser, *args):
    return { key : get_config_val(config_parser, key) for key in args }

def auth_with_pin(client, config_parser):
    auth_url = client.authorization_url('pin')
    webbrowser.open(auth_url)
    pin = input('What is the pin: ')
    response = client.exchange_pin(pin)

    set_config_val_dict(config_parser, {
        'access_token': response[0],
        'refresh_token': response[1],
    })

    return response


def upload_to_imgur(path_name_dict, override=False):
    """Uploads a bunch of images to Imgur.
    
    Arguments:
        path_name_dict {dict} -- (image path, image name) tuple dictionary
    
    Keyword Arguments:
        override {bool} -- If an image with the same name already exists, should it be overwritten? (default: {False})
    
    Returns:
        [list] -- List of Imgur links to uploaded images
    """

    print('\n\nGetting Imgur client...')

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
        print('Refreshing access token')
        access_token = client.refresh_access_token()
        set_config_val(parser, 'access_token', access_token)
    except:
        print('Access token failed to refresh')
        auth_with_pin(client, parser)
        client = pyimgur.Imgur(**get_config_val_dict(parser, 
            'client_id', 'client_secret', 'refresh_token'
        ))

    print('Client retrieved')

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

    links = []
    for img_path, img_name in path_name_dict.items():

        found = False
        for image in album.images:
            if img_name == image.title:
                if override:
                    print('Overriding pre-existing image!')
                    album.remove_images(image)
                else:
                    print('FOUND %s: %s' % (image.title, image.link))
                    links.append(image.link)
                    
                    found = True
                    break
        if found:
            continue

        image = client.upload_image(path=img_path, title=img_name)
        album.add_images(image)
        links.append(image.link)
        print('UPLOADED %s: %s' % (image.title, image.link))

    return links
