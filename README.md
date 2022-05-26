# Foobartory

## How to run:
Requirements:
* Python 3 (written in python 3.10.4)

main.py contains a [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)), so simply running it should be enough on Linux/mac OS (provided the file has execution permission):

``` sh
./main.py
```

If that does not work (also, to run on Windows):

``` sh
python3 -m main
```

## Game settings:
* FPS - simply frames per second. Does not affect the duration of the tasks performed inside the game, but it *does* affect the frequency of game logic updates. Default value is 30.
* TIME_FACTOR - multiplier for all time-based actions in the game. 
1 = real time, default value is 0.1 to avoid waiting for an eternity to see how the game progresses.
* FOOBAR_SUCCESS_RATE - success rate of the foobar creation. Wanted to play around with some values so created a variable for it. Default value is 0.6 (60%) as per instructions.

To change the settings, simply change them in the main.py file. Obviously, this is python, so no compilation required between changes, which makes it simple to keep configuration in code.
