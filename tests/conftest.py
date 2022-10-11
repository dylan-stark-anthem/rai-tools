"""Test configuration.

Note use of `pytest_plugins` to wire up fixtures. This makes it so that we
define fixtures in a module way, scoped close to their use.
"""

pytest_plugins = ["tests.services.data_drift.use_cases.fixtures.simple_scenario"]
