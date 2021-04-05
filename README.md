# Path-Generator
Generates images with block, position, and observations data overlayed. The most recent generated images can be found within `output/`.

All the path images will also be saved in `output/USERNAME/TIME INTERVAL/`.
For example, the images generated for user `Poi` between times `1570000000` and `1582000000` would be stored in `output/Poi/1570000000-1582000000/`.

## Getting Started

### Config
Create a copy of `config-empty.ini` and rename it to `config.ini`. Fill in each field with the proper information.
The values for `world-ids` can be found within the `co_world` table from CoreProtect. The map images within `maps/` should have the same name as the worlds.

<details>
    <summary>Example config.ini</summary>

```ini
[database]
host = 127.0.0.1
database = test
user = test
password = password

[database-tables]
coreprotect_blocks = co_block
coreprotect_users = co_user
coreprotect_worlds = co_world
whimc_positions = whimc_player_positions
whimc_observations = whimc_observations

[imgur]
client_id = xxx
client_secret = xxx
access_token = xxx
refresh_token = xxx
album_id = test

[world-ids]
ColderSun_Cold = 1
ColderSun_HabitableStrip = 2
ColderSun_Hot = 3
EarthControl = 4
NoMoon = 5
TiltedEarth_Frozen = 6
TiltedEarth_JungleIsland = 7
TiltedEarth_Melting = 8
```
</details>

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
$ python runner.py [-h] [-n] [-o] [-e] <username> <start_time> <end_time>
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
