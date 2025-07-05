# Contributing to the BI Documentation Tool

First off, thank you for considering contributing! It's people like you that make this such a great tool.

## How Can I Contribute?

There are many ways to contribute, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or writing code which can be incorporated into the main project.

### Reporting Bugs

- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/user/repo/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/user/repo/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements

- Open a new issue to discuss your enhancement.
- Clearly describe the enhancement and the motivation for it.

### Pull Requests

- Fork the repo and create your branch from `main`.
- If you've added code that should be tested, add tests.
- If you've changed APIs, update the documentation.
- Ensure the test suite passes.
- Make sure your code lints.

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Coding Standards

- We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use type hints for all function signatures.
- Keep lines under 127 characters.

## Branching Strategy

- `main`: This is the primary development branch. All pull requests should be made against this branch.
- `release/vX.X.X`: These branches are for specific releases.
- `feature/your-feature-name`: For new features.
- `fix/your-bug-fix`: For bug fixes.
