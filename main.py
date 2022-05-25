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
    def __init__(self, duration, action, on_after=None):
        self.duration = duration * TIME_FACTOR
        self.action   = action
        self.on_after = on_after

    def run(self, dt):
        def run():
            self.action()
            if self.on_after is not None:
                self.on_after()

        timer = Timer(self.duration, run)
        timer.start()
        return timer


class Robot:
    def __init__(self):
        self.events = []
        self.busy   = False
        self.work   = None


    def foo(self, state):
        def action():
            state['foo'] += 1
            # print('foo')

        self._schedule_event(
            'foo',
            Event(1, action, self._after_action),
            state
        )

    def bar(self, state):
        def action():
            state['bar'] += 1
            # print('bar')

        duration = round(random.uniform(0.5, 2.0), 1)
        self._schedule_event(
            'bar',
            Event(duration, action, self._after_action),
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

            # print('foobar')

        self._schedule_event(
            'foobar',
            Event(2, action, self._after_action),
            state
        )

    def _change_jobs(self, job, state):
        self.work = 'changing'

        def action():
            previous_work = self.work

            self.work = job

            # print(f'switched job from {previous_work} to {self.work}')

        self.events.append(Event(10, action))

    def sell_foobars(self, state):
        state['foobar'] -= 5

        def action():
            state['money'] += 5

        self._schedule_event(
            'selling',
            Event(10, action),
            state
        )

    def buy_new_robot(self, state):
        # TODO: very ugly and just not the way I want it to work.
        if state['foo'] >= 6 and state['money'] >= 3:
            state['money'] -= 3
            state['foo']   -= 6

            spent_money = True

        def action():
            if spent_money:
                state['robots'].append(Robot())

        self._schedule_event(
            'shopping',
            Event(1, action, self._after_action),
            state
        )

    def _after_action(self):
        self.busy = False

    def _schedule_event(self, name, event, state):
        if self.work != name:
            self._change_jobs(name, state)

        self.events.append(event)
        self.busy = True


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
            dt = current_time - last_frame_time
            last_frame_time = current_time

            sleep_time = 1./FPS - (current_time - last_frame_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

            self._game(dt * TIME_FACTOR)
            self.running_events = [e for e in self.running_events if e.is_alive()]

            assert self.state['foo'] >= 0
            assert self.state['foo'] >= 0
            assert self.state['foobar'] >= 0
            assert self.state['money'] >= 0

        for running in self.running_events:
            running.cancel()

        self._refresh_display()
        print('Finished!')

    def _game(self, dt):
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

            # A very elaborate fizzbuzz.
            if self.state['foobar'] >= 10:
                robot.sell_foobars(self.state)
            elif self.state['foo'] > 6 and self.state['bar'] > 6:
                robot.foobar(self.state)
            elif self.state['foo'] >= 10:
                robot.bar(self.state)
            else:
                robot.foo(self.state)

        self._refresh_display()

        if self._win_condition():
            return

        for robot in self.state['robots']:
            if robot.events:
                event = robot.events.pop(0)
                task = event.run(dt)
                self.running_events.append(task)

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

        os.system(CLEAR_COMMAND)
        print(f'Total robots: {total_robots}')
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


INITIAL_GAME_STATE = [Robot(), Robot()]


if __name__ == '__main__':
    game = Game(INITIAL_GAME_STATE)
    game.run()
