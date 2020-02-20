# Path-Generator
Generates images with block, position, and observations data overlayed. The most recent generated images can be found within `output/`.

All the path images will also be saved in `output/USERNAME/TIME INTERVAL/`.
For example, the images generated for user `Poi` between times `1570000000` and `1582000000` would be stored in `output/Poi/1570000000-1582000000/`.

## Getting Started
Modify `config.ini` to contain proper values.

To install all python library dependencies:
```
$ pip3 install -r requirements.txt
```

## Running Path Generator
_**Make sure you're running at least `Python 3.6`.**_

## Local Generator
To locally run the generator and be prompted for a username, start time, and end time:
```
$ python runner.py [-h] [-n] [-o] [-e]
```

### Options
| Option                   | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| `-h`, `--help`           | show the help message and exit                               |
| `-n`, `--no-imgur`       | Do not upload the resulting images to Imgur.                 |
| `-o`, `--overwrite`      | If the path image already exists on Imgur, overwrite it.     |
| `-e`, `--generate-empty` | Still generate a path image even if it has no actions on it. |

## Flask App
To run the Flask App on your local computer:
```
$ python flask_runner.py
```