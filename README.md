# Foobartory

## How to run:
Requirements:
* Python 3 (written in python 3.10.4)

main.py contains a [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)), so simply running it should be enough on Linux/mac OS, maybe even Windows (provided the file has execution permission):

``` sh
./main.py
```

If that does not work:

``` sh
python3 -m main
```

## Rules:
The goal is to code an automatic production line of foobar.

At the beginning, we have 2 robots, each one is able to perform these activities:
* Mining foo : occupy the robot for 1 second.
* Mining bar : keep the robot busy for a random time between 0.5 and 2 seconds.
* Assembling a foobar : keep the robot busy for 2 seconds.
* The robot use a foo and a bar to assemble a foobar.
* The operation has a 60% chance of success.
* In case of failure, the bar can be reused but the foo is lost.
* Sell foobar : take 10s to sell up to 5 foobar , we earn €1 per foobar sold.
* Buying a new robot: take 1s, the robot buy a new robot for €3 and 6 foo.
* Moving to a new activity: occupy the robot for 5 seconds.
* The game stops when you reach 30 robots.

### Notes
1. A second for the robot does not have to be a real life second.
2. Each robot must operate independently, they shouldn’t remain idle.
3. No need to do complex maths to solve the problem, we do not need the action
choice to be optimal, just a working production line.

## Game settings:
* FPS - simply frames per second. Does not affect the duration of the tasks performed inside the game, but it *does* affect the frequency of game logic updates. Default value is 30.
* TIME_FACTOR - multiplier for all time-based actions in the game. 
1 = real time, default value is 0.1 to avoid waiting for an eternity to see how the game progresses.
* FOOBAR_SUCCESS_RATE - success rate of the foobar creation. Wanted to play around with some values so created a variable for it. Default value is 0.6 (60%) as per instructions.
* MAX_ROBOTS - sets the end condition for the game. Once robots count reaches MAX_ROBOTS, the game is finished. Default value is 30.

To change the settings, simply change them in the main.py file. Obviously, this is python, so no compilation required between changes, which makes it simple to keep configuration in code.

## Notes:
clear/cls is used to refresh the display, beware the potential flickering.
