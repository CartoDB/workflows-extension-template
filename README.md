---
title: CARTO Workflows Extension Template
description: Template repository for creating custom extension packages for CARTO Workflows
version: 1.0.0
last-updated: 2025-01-27
depends-on: []
tags: [overview, getting-started, template]
---

# Extension Packages for CARTO Workflows
Use this template repository as a framework for creating extension packages for CARTO Workflows, containing custom components that are tailored to your specific use cases. 

These packages can be easily distributed and installed within the Workflows application, extending its core functionality with new, specialized operations.

![](https://cdn.prod.website-files.com/6345207a1b18e581fcf67604/66507f26948382ff94fa45be_components.jpg)

Find more documentation about installing and managing extension packages in [this section of the CARTO documentation](https://docs.carto.com/carto-user-manual/workflows/extension-packages).

> Currently, Extension Packages are supported in Workflows created for **BigQuery**, **Snowflake**, and **Oracle** connections.

## Documentation

This repository contains comprehensive documentation for both **human developers** and **AI agents**.

### 👤 For Human Developers

Learn more about building, testing, and distributing extension packages:

### 🧬 [Anatomy of an extension package](./doc/anatomy_of_an_extension.md)
This document describes the different elements that are needed to build an extension package and how they relate to each other. 

Read it carefully to understand how inputs, settings and outputs are defined along with the logic of each component.

It also contains a description of the basic elements required to define automated tests for your component.

There are also specific pages that go in detail about some of the pieces needed to build an extension. Check them once you're familiar with the basic structure: 
* [**Extension's metadata**](./doc/extension_metadata.md)
* [**Component's metadata**](./doc/component_metadata.md)
* [**User Defined Functions (UDFs)**](./doc/user_defined_functions.md)
* [**Stored procedure**](./doc/procedure.md)
* [**Icons**](./doc/icons.md)

### ⚙️ [Build you own extension: step by step](./doc/build_your_extension.md)
This section contains a step by step guide for creating your first extension package. 

### ✅ [Tests](./doc/running_tests.md)
Learn how to configure, run and automate different tests for your components.

### 🧰 [Tools](./doc/tooling.md)
Learn how to use the tools included with this template to help with the creation of extension packages.

---

### 🤖 For AI Agents

This repo ships a **Claude Code skill** at [`.claude/skills/build-workflows-extension/`](./.claude/skills/build-workflows-extension/SKILL.md) that autoloads when an agent is asked to build, modify, test, or package an extension. The skill is the single entry point — its `SKILL.md` walks the agent through the five-phase lifecycle (scaffold → metadata → SQL → tests → package/deploy) and points at deeper references on demand.

Agent-targeted reference material has been moved into the skill folder:

**Quick Start:**
- [**Quickstart Guide**](./.claude/skills/build-workflows-extension/references/quickstart.md) - Minimal 5-minute path to first component
- [**Quick Reference**](./.claude/skills/build-workflows-extension/references/quick-reference.md) - One-page cheat sheet with patterns and commands
- [**Glossary**](./.claude/skills/build-workflows-extension/references/glossary.md) - All domain terms and definitions

**Reference:**
- [**Validation Rules**](./.claude/skills/build-workflows-extension/references/validation-rules.md) - Complete constraints in scannable tables
- [**Extension Metadata Schema**](./.claude/skills/build-workflows-extension/references/extension-metadata-schema.json) - JSON Schema for validation
- [**Component Metadata Schema**](./.claude/skills/build-workflows-extension/references/component-metadata-schema.json) - JSON Schema for validation

**Examples:**
- [**Examples Index**](./.claude/skills/build-workflows-extension/examples/README.md) - Working component examples with tests
  - [Minimal Component](./.claude/skills/build-workflows-extension/examples/01-minimal-component/) - Complete working example
  - [Multi-Input Component](./.claude/skills/build-workflows-extension/examples/02-multi-input-component/) - All input types
  - [Conditional Inputs](./.claude/skills/build-workflows-extension/examples/03-conditional-inputs/) - ShowIf patterns

**Patterns:**
- [**Template SQL (Annotated)**](./components/template/src/) - Heavily commented fullrun.sql and dryrun.sql explaining patterns

**Navigation Tips for Agents:**
- Start at `SKILL.md` — it indexes everything else
- Reference JSON Schemas for metadata validation
- Use the Quick Reference for fast lookups during edits