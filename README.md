# Path-Generator
Generates images with block, position, and observations data overlayed. The most recent generated images can be found within `output/`.

All the path images will also be saved in `output/USERNAME/TIME INTERVAL/`.

## Getting started
Make sure you're running at least `Python 3.6`.

Modify `config.ini` to contain proper values.

Run `pip install -r requirements.txt` to install all python requirements.

## Running path generator
To locally run the generator and be prompted for a username, start time, and end time.
```
python runner.py
```

To run the Flask App on your local computer:
```
python flask_runner.py
```