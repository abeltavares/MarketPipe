# Contributing to MarketPipe  🚀

First off, thank you for considering contributing to MarketPipe! It's people like you that make MarketPipe such a great tool.

## Open Development 🌍

All work on MarketPipe happens directly on [GitHub](https://github.com/abeltavares/marketpipe). Both core team members and external contributors send pull requests which go through the same review process.

## Branch Organization 🌲

We will do our best to keep the [`main`](https://github.com/abeltavares/marketpipe/tree/main) branch in good shape, with tests passing at all times. If you're looking for a task to contribute to, check out the issues tagged with `ready_for_development`.


## Reporting Bugs 🐞

If you encounter a problem with MarketPipe, you are welcome to open an issue. Before that, please make sure to check if an issue doesn't already exist.

**Great Bug Reports** need to have:

- A quick summary and/or background.
- Steps to reproduce.
  - Be specific!
  - Give sample code if you can.
- What you expected would happen.
- What actually happens.
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work).

## Feature Requests 💡

Feature requests are welcome. But take a moment to find out whether your idea fits with the scope and aims of the project. It's up to *you* to make a strong case to convince the project's developers of the merits of this feature. Please provide as much detail and context as possible.

## Pull Requests ✨

**Working on your first Pull Request?** You can learn on [How to Contribute to an Open Source Project on GitHub](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)

Here's a quick rundown of the process:

1. Fork the repository and create your branch from `main`.
2. Always create a new branch for your work.
3. If you've added code that should be tested, add tests.
4. If you've changed functionality and use of marketpipe, update the documentation.
5. Ensure the test suite passes (defined in `pre-commit`).
6. Make sure your code lints (defined in `pre-commit`).
7. Issue that pull request!


To ensure code quality and run unit tests and runs black linter before committing changes, MarketTrackPipe uses [pre-commit](https://pre-commit.com/) hooks. 

 Additionally, these tests are also executed in a GitHub Actions workflow on every pull request to the repository.

## Get Started 🚦

Ready to start? Make sure to setup your environment:

1. **Create a Virtual Environment** (Recommended): A virtual environment helps manage dependencies and keeps your system tidy. Here's how you can set one up:

   ```bash
   python3 -m venv marketpipe-env
   source marketpipe-env/bin/activate
   
2. **Install Dependencies**: MarketPipe comes with a `requirements.txt` file that lists all the Python packages needed for the project. Install them using:  
   ```bash
   pip install -r requirements.txt

3. **Install Docker**: You can install Docker from [here](https://docs.docker.com/get-docker/).

4. **Install Pre-commit**: Pre-commit is a tool to help you manage your git pre-commit hooks. You can install it using:
   ```bash
   pre-commit install