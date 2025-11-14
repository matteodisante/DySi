Developer Documentation
=======================

Documentation for developers working on the rocket simulation framework.

.. toctree::
   :maxdepth: 2
   :caption: Developer Guides
   
   architecture
   module_reference
   
Overview
--------

This section contains technical documentation for understanding and contributing to the codebase.

System Architecture
-------------------

The :ref:`developer-architecture` page provides a comprehensive overview of the system design:

- **Layered architecture** from YAML config to simulation outputs
- **Data flow diagrams** showing the complete pipeline
- **Design patterns** used throughout the codebase
- **Module responsibilities** and extension points

Key topics covered:

- Configuration loading and validation
- Builder pattern for object construction
- Flight simulation execution
- Output generation (CSV, JSON, plots)
- Performance considerations
- Testing strategy

Module Quick Reference
----------------------

The :ref:`developer-module-reference` page is a practical cheat sheet for all 13 core modules:

- **Quick lookup table** showing each module's purpose, inputs, and outputs
- **Dependency hierarchy** (Level 0-5) to understand module relationships
- **Code examples** for common tasks with each module
- **Typical workflows** showing how modules work together
- **Quick tips** for finding the right module for your task

This is your go-to reference when you need to quickly remember "which module does what" or see practical code examples.

Additional Resources
--------------------

For additional developer documentation, see the files in ``docs/developer/``:

- ``ARCHITECTURE.md`` - Original detailed architecture document
- ``API_REFERENCE.md`` - Complete API documentation
- ``MODULE_REFERENCE.md`` - Module-level documentation
- ``CONTRIBUTING.md`` - Contributing guidelines
- ``MOTOR_ATTRIBUTES_CLASSIFICATION.md`` - RocketPy motor attributes

.. note::
   
   The architecture documentation in this section provides a high-level overview.
   For low-level implementation details, refer to the Markdown files in ``docs/developer/``.
