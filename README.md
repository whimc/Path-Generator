# Path-Generator
Generates images with block, position, and observations data overlayed. The most recent generated images can be found within `output/`.

All the path images will also be saved in `output/USERNAME/TIME INTERVAL/`.
For example, the images generated for user `Poi` between times `1570000000` and `1582000000` would be stored in `output/Poi/1570000000-1582000000/`.

## Getting Started

### Config

**If you are still using a `.ini` config, run `python -m pathgenerator.utils.convert_config` to convert it to the new JSON format!**

Create a copy of `config-sample.json` and rename it to `config.json`. Fill in each field with the proper information.

If you are using downloads of our worlds, the only part of the `worlds` section you have to modify is the `coreprotect_id` field.

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

To install all python library dependencies (run from command line, NOT python shell):
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

# Installation and Map Updates
Can be found in [setup_update.md](https://github.com/whimc/Path-Generator/setup_update.md)

# Running Path Generator

## Local Generator
To locally run the generator:
```
$ python -m pathgenerator [-h] [-n] [-o] [-e] <username> <start_time> <end_time>
```

## Exploration Metrics
Exploration metrics 'draw' a 10x10 grid on maps. If a user explores one of those tiles or makes an observation on them,
it is marked. The sum of marked tiles is taken and a CSV is created. To get these metrics, run the following:
```
$ python -m pathgenerator.exploration_metric <position output file> <observation output file> <start time> <end time> <username> [usernames ...]
```
If you don't think in terms of 10 digit Unix time you can use [a converter like this](https://www.unixtimestamp.com/index.php) to create your time stamps. DO include file extensions (.csv) on the back of your file names. When exporting on the WHIMC AWS instance you will need to run the command as sudo for permission, from inside of the directory, which is path-generator. In this case you also need to use python3 instead of just python. An example command on the WHIMC AWS instance looks like:
```
$ cd path-generator
$ sudo python3 -m pathgenerator.exploration_metric position.csv observation.csv 1649231449 1652255449 MCSoctopus MCSnarwhal MCSmouse MCSlion MCSiguana MCSarmadillo MCSbear MCScobra MCSdolphin MCSeagle MCSfox MCSgecko MCShorse MCSjackal MCSkangarooo
```
Once you've generated your files you'll need to transport them off of the AWS instance to a computer for analysis. One way to do this is via [SSH and WinSCP](https://winscp.net/eng/docs/guide_amazon_ec2). Our current UIUC AWS instance is:
```
ec2-3-140-198-187.us-east-2.compute.amazonaws.com
```
Username ubuntu should work.

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
