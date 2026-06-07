"""QADE-local interfaces used for standalone extraction.

The classes subclass repository-level core abstractions when available, so
existing integration tests that check against ``core.abstractions`` remain
compatible. In an extracted QADE package, they fall back to local ABCs.
"""

from abc import ABC, abstractmethod

try:
    from core.abstractions.base_critic import BaseCritic as _CoreBaseCritic
    from core.abstractions.base_hypothesis_generator import (
        BaseHypothesisGenerator as _CoreBaseHypothesisGenerator,
    )
    from core.abstractions.base_memory import BaseMemory as _CoreBaseMemory
    from core.abstractions.base_sandbox import BaseSandbox as _CoreBaseSandbox
except Exception:
    _CoreBaseCritic = ABC
    _CoreBaseHypothesisGenerator = ABC
    _CoreBaseMemory = ABC
    _CoreBaseSandbox = ABC


class BaseCritic(_CoreBaseCritic):
    if _CoreBaseCritic is ABC:

        @abstractmethod
        def validate(self, *args, **kwargs):
            pass


class BaseSandbox(_CoreBaseSandbox):
    if _CoreBaseSandbox is ABC:

        @abstractmethod
        def execute(self, *args, **kwargs):
            pass


class BaseMemory(_CoreBaseMemory):
    if _CoreBaseMemory is ABC:

        @abstractmethod
        def store(self, *args, **kwargs):
            pass

        @abstractmethod
        def retrieve(self, *args, **kwargs):
            pass


class BaseHypothesisGenerator(_CoreBaseHypothesisGenerator):
    if _CoreBaseHypothesisGenerator is ABC:

        @abstractmethod
        def propose(self, *args, **kwargs):
            pass

        @abstractmethod
        def mutate(self, *args, **kwargs):
            pass

