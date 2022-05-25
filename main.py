#! /usr/bin/env python

import time
import random
from threading import Timer


FPS                 = 1
TIME_FACTOR         = .1
FOOBAR_SUCCESS_RATE = 0.6


class Event:
    def __init__(self, duration, action):
        self.duration = duration * TIME_FACTOR
        self.action   = action

    def run(self, dt):
        timer = Timer(self.duration, self.action)
        timer.start()


class Robot:
    def __init__(self):
        self.busy = False
        self.work = 'mining'
        self.times_worked_current = 0

    def foo(self, state):
        self.busy = True
        self.times_worked_current += 1

        def action():
            state['foo'] += 1
            self._cleanup()
            print('foo')

        return Event(1, action)


    def bar(self, state):
        self.busy = True
        self.times_worked_current += 1

        duration = round(random.uniform(0.5, 2.0), 1)

        def action():
            state['bar'] += 1
            self._cleanup()
            print('bar')

        return Event(duration, action)


    def foobar(self, state):
        duration = 2
        self.times_worked_current += 1

        def action():
            success = random.uniform(0., 1.0)
            if success > FOOBAR_SUCCESS_RATE:
                if state['foo'] > 0:
                    state['foo'] -= 1
                    state['bar'] -= 1
                    state['foobar'] += 1
                    print('SUCCESS!!')
            else:
                if state['foo'] > 0:
                    state['foo'] -= 1
                    print('failure :(')
            self._cleanup()
            print('foobar')

        return Event(duration, action)


    def change_jobs(self, state):
        def action():
            previous_work = self.work

            self.work = 'shopping' if self.work == 'mining' else 'mining'
            self.times_worked_current = 0

            print(f'switched job from {previous_work} to {self.work}')

        return Event(10, action)


    def buy_new_robot(self, state):
        # TODO: very ugly and just not the way I want it to work.
        if state['foo'] >= 6 and state['money'] >= 3:
            state['foo'] -= 6
            state['money'] -= 3
            spent_money = True

        def action():
            if spent_money:
                state['robots'].append(Robot())

        self.times_worked_current += 1

        return Event(1, action)


    def _cleanup(self):
        self.busy = False


class Market:
    def __init__(self):
        self.busy = False


    def sell_foobars(self, state):
        # TODO: sell continuously, somehow
        def action():
            if state['foobar'] >= 5:
                state['foobar'] -= 5
                state['money'] += 5

        return Event(10, action)


class Game:
    def __init__(self, initial_robots):
        self.market = Market()
        self.moves  = 0

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
        while not self._winning_condition():
            current_time = time.time()
            dt = current_time - last_frame_time
            last_frame_time = current_time

            sleep_time = 1./FPS - (current_time - last_frame_time)
            if sleep_time > 0:
                time.sleep(sleep_time * TIME_FACTOR)

            self._game(dt * TIME_FACTOR)

        print('State at the end of the game:')
        print(self.state)
        print(f'Finished in {self.moves} moves.')


    def _game(self, dt):
        events = []

        # Start moving robots to shopping if there enough resources are
        # being collected.
        if self.state['money'] >= 3 and self.state['foo'] >= 6:
            shopping_robots = [r for r in self._available_robots() if r.work == 'shopping']

            if shopping_robots:
                shopping_robot = shopping_robots[0]
                event = shopping_robot.buy_new_robot(self.state)
                events.append(event)
            else:
                robot = self.state['robots'][0]
                event = robot.change_jobs(self.state)
                events.append(event)

        # Handle mining here. Don't want the robots to get bored,
        # so switch them between jobs after enough turns doing the same work.
        for robot in self._available_robots():
            if robot.work == 'shopping': continue

            if robot.times_worked_current >= 10:
                event = robot.change_jobs(self.state)
                events.append(event)
                continue

            # The numbers were chosen completely by trial-and-error.
            if self.state['foo'] > 6 and self.state['bar'] > 6:
                event = robot.foobar(self.state)
            elif self.state['foo'] >= 10:
                event = robot.bar(self.state)
            else:
                event = robot.foo(self.state)

            events.append(event)

        # Sell, sell, sell.
        if self.state['foobar'] >= 10 and (not self.market.busy):
            event = self.market.sell_foobars(self.state)
            events.append(event)

        self.moves += 1

        if self._winning_condition():
            return

        while len(events) > 0:
            event = events.pop()
            event.run(dt)

        print(self.state)


    def _winning_condition(self):
        return len(self.state['robots']) >= 30


    def _available_robots(self):
        return [r for r in self.state['robots'] if not r.busy]


INITIAL_GAME_STATE = [Robot(), Robot()]


if __name__ == '__main__':
    game = Game(INITIAL_GAME_STATE)
    game.run()
