# How to Contribute to raitools

This guide covers many important topics for contributing to the development of `raitools`:

- [Style guide & documentation](#style-guide--documentation)
- [Development](#development)


## Style guide & documentation

We follow [Google's style guide](https://google.github.io/styleguide/pyguide.html) and [Google's documentation style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for our docs.
Of course there will always be exceptions, which we'll implement directly via the reformatter, style guide checker, and static analyzer, or some other part of our build system (e.g., [black](https://github.com/psf/black) and [flake8](https://flake8.pycqa.org/en/latest/)).
And whatever we can't codify, we'll note here.

### A note on Markdown

Keep Markdown clean:
Assume someone is going to be reading the text directly, without it being rendered in a browser.
Make their life easier by using newlines to separate section headers from text, etc.

Keep Markdown simple:
There is almost never a reason to use HTML directly - the entire point of Markdown is so we don't need to.

## Development

In general, development requires `poetry` for package/dependency management, `Make` for CI orchestration, and `pre-commit` for managing Git hooks.

The best and fastest way to get started with a base development environment is to use the provided [VSCODE development container](https://code.visualstudio.com/docs/remote/containers).
This will take care of all system-level dependencies (e.g., SSL certs, utilities, etc.) and project-level setup (e.g., pre-commit and poetry installs).

Once in the dev container, you have the general requirements installed and all you need to do to start is to run

```
make build
```
