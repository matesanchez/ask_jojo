"""jojo_core — shared primitives for JoJo Bot v2.0.

Houses config loading (including the Anthropic-client factory once keys
are provisioned), logging, filesystem path helpers, and the Redis/RQ
wiring. Every other jojo_* package imports from here. Populated
progressively from Phase 1 onward; Phase 0 is skeleton only.
"""

__version__ = "0.1.0"
