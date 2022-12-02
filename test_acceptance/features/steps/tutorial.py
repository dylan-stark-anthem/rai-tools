"""Acceptance test steps."""

from behave import given, then, when
from behave.runner import Context


@given("we have behave installed")
def step_impl(context: Context) -> None:
    """Takes step."""
    pass


@when("we implement a test")
def when_impl(context: Context) -> None:
    """Takes step."""
    assert True is not False


@then("behave will test it for us!")
def then_impl(context: Context) -> None:
    """Takes step."""
    assert context.failed is False
