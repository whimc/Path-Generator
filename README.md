# Path-Generator
Generates images with block, position, and observations data overlayed. The most recent generated images can be found within `output/`.

All the path images will also be saved in `output/USERNAME/TIME INTERVAL/`.
For example, the images generated for user `Poi` between times `1570000000` and `1582000000` would be stored in `output/Poi/1570000000-1582000000/`.

## Getting Started

### Config

**If you are still using a `.ini` config, run `python -m pathgenerator.convert_config` to convert it to the new JSON format!**

Create a copy of `config-sample.json` and rename it to `config.json`. Fill in each field with the proper information.

**Currently, world images _must_ be 1024x1024!**

#### World Attributes

| Key | Required | Type | Default | Description |
|-|-|-|-|-|
| `display_name` | Yes | String | `n/a` | The name of the world that will be used for display purposes |
| `world_name` | Yes | String | `n/a` | The name of the Minecraft world |
| `coreprotect_id` | Yes | Integer | `n/a` | The ID of the world within CoreProtect |
| `image_path` | Yes | String | `n/a` | Path to the image for this world |
| `pixel_to_block_ratio` | No | Float | `1.0` | Ratio of pixels to blocks within the image |
| `top_left_coordinate_x` | No | Integer | `-512` | The X coordinate (in Minecraft) of the top left pixel |
| `top_left_coordinate_z` | No | Integer | `-512` | The Z coordinate (in Minecraft) of the top left pixel |

### Dependencies

#### External dependencies
1. [CoreProtect](https://www.spigotmc.org/resources/coreprotect.8631/)
2. [WHIMC-ObservationDisplayer](https://github.com/whimc/Observation-Displayer)
3. [WHIMC-PositionTracker](https://github.com/whimc/Position-Tracker)

These plugins must all be configured to write to the same **MySQL** database. This service will not work otherwise.

#### Python dependencies
_**Make sure you're running at least `Python 3.6`.**_

To install all python library dependencies:
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

# Running Path Generator

## Local Generator
To locally run the generator:
```
$ python -m pathgenerator [-h] [-n] [-o] [-e] <username> <start_time> <end_time>
```

### Options
| Option                   | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| `-h`, `--help`           | show the help message and exit                               |
| `-n`, `--no-imgur`       | Do not upload the resulting images to Imgur.                 |
| `-o`, `--overwrite`      | If the path image already exists on Imgur, overwrite it.     |
| `-e`, `--generate-empty` | Still generate a path image even if it has no actions on it. |

## Flask App

### Running locally
To run the Flask App on your local computer:
```
$ python -m pathgenerator.api
```

### Running on Linux server
Follow the [install guide](./install.md) to host the API on a Linux server.
