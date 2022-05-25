#! /usr/bin/env python

import os
import time
import random
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
        # Use on before to set the Robot.busy to True
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


class Robot:
    def __init__(self):
        self.events = []
        self.busy   = False
        self.work   = 'foo'

    def foo(self, state):
        def action():
            state['foo'] += 1

        self._schedule_event(
            'foo',
            self._create_event(1, action),
            state
        )

    def bar(self, state):
        def action():
            state['bar'] += 1

        duration = round(random.uniform(0.5, 2.0), 1)
        self._schedule_event(
            'bar',
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
            'foobar',
            self._create_event(2, action),
            state
        )

    def sell_foobars(self, state):
        state['foobar'] -= 5

        for _ in range(5):
            def action():
                state['money'] += 1

            self._schedule_event(
                'selling',
                self._create_event(2, action),
                state
            )

    def buy_new_robot(self, state):
        state['money'] -= 3
        state['foo']   -= 6

        def action():
            state['robots'].append(Robot())

        self._schedule_event(
            'shopping',
            self._create_event(1, action),
            state
        )

    def _change_jobs(self, job):
        self.work = 'changing'

        def action():
            self.work = job

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
            self._change_jobs(name)

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

            self._game()
            self.running_events = [e for e in self.running_events if e.is_alive()]
            self._assert_state()

        for running in self.running_events:
            running.cancel()

        self._refresh_display()
        print('Finished!')

    def _game(self):
        # Start moving robots to shopping if enough resources are
        # being collected.
        if self.state['money'] >= 3 and self.state['foo'] >= 6:
            shopping_robots = [r for r in self._available_robots() if r.work == 'shopping']

            if shopping_robots:
                robot = shopping_robots[0]
            else:
                robot = self.state['robots'][0]

            robot.buy_new_robot(self.state)

        # Handle mining here. Don't want the robots to get bored,
        # so switch them between jobs after enough turns doing the same work.
        for robot in self._available_robots():
            if robot.work == 'shopping':
                continue

            if robot.busy:
                continue

            if robot.events:
                continue

            # Fizzbuzz!
            if self.state['foobar'] >= 10:
                robot.sell_foobars(self.state)
            elif self.state['foo'] >= 8 and self.state['bar'] >= 2:
                robot.foobar(self.state)
            elif self.state['foo'] >= 10:
                robot.bar(self.state)
            else:
                robot.foo(self.state)

        for robot in self.state['robots']:
            if robot.busy:
                continue

            if robot.events:
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

    def _worker_count(self, job):
        return len([r for r in self.state['robots'] if r.work == job])

    def _refresh_display(self):
        total_robots = len(self.state['robots'])
        foo          = self._worker_count('foo')
        bar          = self._worker_count('bar')
        foobar       = self._worker_count('foobar')
        shopping     = self._worker_count('shopping')
        selling      = self._worker_count('selling')
        changing     = self._worker_count('changing')

        assert foo + bar + foobar + shopping + selling + changing == total_robots

        os.system(CLEAR_COMMAND)
        print(f'Total robots: {total_robots}\n')
        print(f'Mining foo: {foo}')
        print(f'Mining bar: {bar}')
        print(f'Mining foobar: {foobar}')
        print(f'Shopping: {shopping}')
        print(f'Selling foobars: {selling}')
        print(f'Changing jobs: {changing}\n')

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


INITIAL_GAME_STATE = [Robot(), Robot()]


if __name__ == '__main__':
    game = Game(INITIAL_GAME_STATE)
    game.run()
