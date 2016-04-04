#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.append("../metrika_runner")
from metrika_engine import MetrikaEngine
from GameOutliner import GameOutliner

__author__ = 'Javier Pimás'

if __name__ == '__main__':

    outliner = GameOutliner()
    engine = MetrikaEngine(outliner)
    engine.go()

