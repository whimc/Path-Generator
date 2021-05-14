from argparse import ArgumentParser

from pathgenerator.runner import get_path_links

def run():
    parser = ArgumentParser(prog='pathgenerator')
    parser.add_argument('username', type=str, help='Username of the player')
    parser.add_argument('start_time', type=int, help='Unix start time')
    parser.add_argument('end_time', type=int, help='Unix end time')
    parser.add_argument('-n', '--no-imgur', action='store_true', dest='no_imgur',
                        help='Do not upload the resulting images to Imgur.')
    parser.add_argument('-o', '--overwrite', action='store_true', dest='overwrite',
                        help='If the path image already exists on Imgur, overwrite it.')
    parser.add_argument('-e', '--generate-empty', action='store_true', dest='gen_empty',
                        help='Still generate a path image even if it has no actions on it.')

    options = vars(parser.parse_args())

    links = get_path_links(**options)
    if not links:
        exit()

    print('\nLinks:')
    padding = len(max(links.keys(), key=len)) + 1
    for name, link in links.items():
        print(f'\t{name:<{padding}} -> {link}')

run()
