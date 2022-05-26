#! /usr/bin/env python

import os
import time
import random
from enum import Enum
from sys import platform
from threading import Timer


if platform == "win32":
    CLEAR_COMMAND = 'cls'
else:
    CLEAR_COMMAND = 'clear'


FPS                 = 60
TIME_FACTOR         = .1
FOOBAR_SUCCESS_RATE = 0.6


class Event:
    def __init__(self, duration, action, on_before, on_after=None):
        self.duration  = duration * TIME_FACTOR
        self.action    = action
        self.on_before = on_before
        self.on_after  = on_after

    def run(self):
        # Use on_before to set the Robot.busy to True
        # on run, instead of on creating the event.
        # This avoids the issue where multiple events are
        # started before busy is set to True, which is
        # obviously incorrect.
        self.on_before()

        def run_action():
            self.action()
            if self.on_after is not None:
                self.on_after()

        timer = Timer(self.duration, run_action)
        timer.start()
        return timer


class RobotWork(Enum):
    UNASSIGNED = 0
    FOO = 1,
    BAR = 2,
    FOOBAR = 3
    SHOPPING = 4,
    SELLING = 5,
    CHANGING = 6


class Robot:
    def __init__(self, initial_work=RobotWork.UNASSIGNED):
        self.events = []
        self.busy   = False
        self.work   = initial_work

    def foo(self, state):
        def action():
            state['foo'] += 1

        self._schedule_event(
            RobotWork.FOO,
            self._create_event(1, action),
            state
        )

    def bar(self, state):
        def action():
            state['bar'] += 1

        duration = round(random.uniform(0.5, 2.0), 1)
        self._schedule_event(
            RobotWork.BAR,
            self._create_event(duration, action),
            state
        )

    def foobar(self, state):
        # Only ever remove items in synchronous actions.
        state['foo'] -= 1
        state['bar'] -= 1

        def action():
            success = random.uniform(0., 1.0)

            if success > FOOBAR_SUCCESS_RATE:
                state['foobar'] += 1
            else:
                state['bar'] += 1

        self._schedule_event(
            RobotWork.FOOBAR,
            self._create_event(2, action),
            state
        )

    def sell_foobars(self, state):
        state['foobar'] -= 5

        for _ in range(5):
            def action():
                state['money'] += 1

            self._schedule_event(
                RobotWork.SELLING,
                self._create_event(2, action),
                state
            )

    def buy_new_robot(self, state):
        state['money'] -= 3
        state['foo']   -= 6

        def action():
            state['robots'].append(Robot())

        self._schedule_event(
            RobotWork.SHOPPING,
            self._create_event(1, action),
            state
        )

    # All methods below are candidates for moving
    # into a base class. Not doing that until needed.

    def _change_work(self, work):
        self.work = RobotWork.CHANGING

        def action():
            self.work = work

        self.events.append(
            self._create_event(5, action)
        )

    def _create_event(self, duration, action):
        return Event(duration, action, self._before_action, self._after_action)

    def _before_action(self):
        self.busy = True

    def _after_action(self):
        self.busy = False

    def _schedule_event(self, name, event, state):
        if self.work != name:
            self._change_work(name)

        self.events.append(event)


class Game:
    def __init__(self, initial_robots):
        self.running_events = []

        self.state = {
            'robots': initial_robots,
            'foo':    0,
            'bar':    0,
            'foobar': 0,
            'money':  0
        }

    def run(self):
        last_frame_time = time.time()

        # simple game loop
        while not self._win_condition():
            current_time = time.time()
            # dt = current_time - last_frame_time
            last_frame_time = current_time

            sleep_time = 1./FPS - (current_time - last_frame_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

            # No graceful exit for you!

            self._game()
            self.running_events = [e for e in self.running_events if e.is_alive()]
            self._assert_state()

        for running in self.running_events:
            running.cancel()

        self._refresh_display()
        print('Finished!')

    def _game(self):
        # TODO: the focus should be to have the smallest amount of work changes.
        # Queue up the actions.
        # Robot actions are maybe better defined as separate RobotBehavior
        # or something similar, but trying to keep it simple here.
        for robot in self._available_robots():
            if robot.busy:
                continue

            if robot.events:
                continue

            # Fizzbuzz!
            # The values for the conditions were
            # chosen completely arbitrarily.
            # Hope softlocks are not possible!
            if self.state['money'] >= 3 and self.state['foo'] >= 6:
                robot.buy_new_robot(self.state)
            elif self.state['foobar'] >= 5:
                robot.sell_foobars(self.state)
            elif self.state['foo'] >= 8 and self.state['bar'] >= 2:
                robot.foobar(self.state)
            elif self.state['foo'] >= 10:
                robot.bar(self.state)
            else:
                robot.foo(self.state)

        # TODO: not sure if it even makes sense to loop through
        # robots twice.
        # Execute the actions
        for robot in self.state['robots']:
            if robot.busy:
                continue

            if robot.events:
                # Treat robot events as a stack.
                # Works well in case of changing work,
                # WOrk change and the next work are pushed to the stack.
                # First the work change will be executed, then the work.
                event = robot.events.pop(0)
                task = event.run()
                self.running_events.append(task)

        self._refresh_display()

        if self._win_condition():
            return

    def _win_condition(self):
        return len(self.state['robots']) >= 30

    def _available_robots(self):
        return [r for r in self.state['robots'] if not r.busy]

    def _worker_count(self, work):
        return len([r for r in self.state['robots'] if r.work == work])

    def _refresh_display(self):
        # Horribly inefficient
        total_robots = len(self.state['robots'])
        unassigned   = self._worker_count(RobotWork.UNASSIGNED)
        foo          = self._worker_count(RobotWork.FOO)
        bar          = self._worker_count(RobotWork.BAR)
        foobar       = self._worker_count(RobotWork.FOOBAR)
        shopping     = self._worker_count(RobotWork.SHOPPING)
        selling      = self._worker_count(RobotWork.SELLING)
        changing     = self._worker_count(RobotWork.CHANGING)

        assert unassigned + foo + bar + foobar + shopping + selling + changing == total_robots

        # Bad, but, zero dependencies.
        os.system(CLEAR_COMMAND)
        print(f'Total robots: {total_robots}\n')
        print(f'Mining foo: {foo}')
        print(f'Mining bar: {bar}')
        print(f'Mining foobar: {foobar}')
        print(f'Shopping: {shopping}')
        print(f'Selling foobars: {selling}')
        print(f'Changing work: {changing}\n')

        print({
            'foo':    self.state['foo'],
            'bar':    self.state['bar'],
            'foobar': self.state['foobar'],
            'money':  self.state['money']
        })

    def _assert_state(self):
        assert self.state['foo'] >= 0
        assert self.state['foo'] >= 0
        assert self.state['foobar'] >= 0
        assert self.state['money'] >= 0


INITIAL_GAME_STATE = [Robot(RobotWork.FOO), Robot(RobotWork.FOO)]


if __name__ == '__main__':
    game = Game(INITIAL_GAME_STATE)
    game.run()
