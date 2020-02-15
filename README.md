# Path-Generator
Generates images with block, position, and observations data overlayed. The most recent generated images can be found within `output/`.

All the path images will also be saved in `output/USERNAME/TIME INTERVAL/`.

## Getting started
Modify `config.ini` to contain proper values.

To install all python library dependencies:
```
pip3 install -r requirements.txt
```

## Running path generator
_**Make sure you're running at least `Python 3.6`.**_

To locally run the generator and be prompted for a username, start time, and end time.
```
python runner.py
```

To run the Flask App on your local computer:
```
python flask_runner.py
```