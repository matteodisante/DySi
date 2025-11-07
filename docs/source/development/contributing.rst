Contributing
============

Thank you for considering contributing to the rocket simulation framework!

Getting Started
---------------

1. Fork the Repository
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone https://github.com/YOUR_USERNAME/rocket-sim.git
    cd rocket-sim

2. Create Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

3. Create a Branch
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git checkout -b feature/my-new-feature

Development Workflow
--------------------

1. Make Changes
~~~~~~~~~~~~~~~

- Write clean, documented code
- Follow the code style guide
- Add tests for new functionality

2. Run Tests
~~~~~~~~~~~~

.. code-block:: bash

    pytest tests/

3. Check Code Style
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Format code
    black src/ scripts/ tests/

    # Check linting
    flake8 src/ scripts/ tests/

    # Type checking
    mypy src/

4. Update Documentation
~~~~~~~~~~~~~~~~~~~~~~~

If you added new features:

.. code-block:: bash

    cd docs
    make html
    # Open docs/build/html/index.html to preview

5. Commit Changes
~~~~~~~~~~~~~~~~~

Write descriptive commit messages:

.. code-block:: bash

    git add .
    git commit -m "Add feature: description of what you did"

6. Push and Create PR
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git push origin feature/my-new-feature

Then create a Pull Request on GitHub.

Types of Contributions
----------------------

Bug Fixes
~~~~~~~~~

- Check existing issues first
- Include test that reproduces the bug
- Reference issue number in commit

New Features
~~~~~~~~~~~~

- Discuss in an issue before major changes
- Include documentation and tests
- Update configuration reference if needed

Documentation
~~~~~~~~~~~~~

- Fix typos or clarify existing docs
- Add examples
- Improve API documentation

Testing
~~~~~~~

- Add tests for uncovered code
- Improve test coverage
- Add integration tests

Code Review Process
-------------------

1. **Automated Checks**: CI runs tests and linting
2. **Maintainer Review**: A maintainer reviews your code
3. **Feedback**: Address any requested changes
4. **Merge**: Once approved, your PR is merged

Guidelines
----------

Code Quality
~~~~~~~~~~~~

- **Type hints**: Use type annotations
- **Docstrings**: Document all public APIs (NumPy style)
- **Comments**: Explain "why", not "what"
- **Tests**: Aim for >80% coverage

Compatibility
~~~~~~~~~~~~~

- **RocketPy**: Maintain compatibility with RocketPy API
- **Python**: Support Python 3.8+
- **Dependencies**: Minimize new dependencies

Performance
~~~~~~~~~~~

- **Profile**: Measure before optimizing
- **Parallel**: Use multiprocessing for Monte Carlo
- **Memory**: Avoid loading entire datasets in memory

Reporting Issues
----------------

Bug Reports
~~~~~~~~~~~

Include:

- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Configuration file (if applicable)
- Python version and OS

Feature Requests
~~~~~~~~~~~~~~~~

Include:

- Use case description
- Proposed API or interface
- Example configuration or usage

Questions
~~~~~~~~~

- Check documentation first
- Search existing issues
- Ask specific, detailed questions

Community
---------

- **Be Respectful**: Treat all contributors with respect
- **Be Constructive**: Provide helpful feedback
- **Be Patient**: Reviews take time

License
-------

By contributing, you agree that your contributions will be licensed under the same license as the project.

Next Steps
----------

- :doc:`architecture` - Understand the codebase
- :doc:`testing` - Learn about testing
- :doc:`code_style` - Follow coding standards
