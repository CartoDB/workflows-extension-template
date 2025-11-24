---
title: Examples Index
description: Collection of pedagogical examples demonstrating component patterns
version: 1.0.0
last-updated: 2025-01-27
depends-on: [component_metadata.md, procedure.md]
tags: [examples, patterns, tutorial]
---

# Component Examples

This folder contains minimal, pedagogical examples demonstrating common patterns for building CARTO Workflows components.

## Overview

| Example | Focus | Files | Complexity |
|---------|-------|-------|------------|
| [01-minimal-component](#01-minimal-component) | Complete working component with tests | All | Beginner |
| [02-multi-input-component](#02-multi-input-component) | Various input types | Metadata only | Intermediate |
| [03-conditional-inputs](#03-conditional-inputs) | Dynamic UI with showIf | Metadata only | Intermediate |

---

## 01-minimal-component

**Purpose:** The simplest possible working component - adds a constant column to a table.

**What it demonstrates:**
- Basic component structure
- Table input/output
- Single string input parameter
- SQL pattern for augmenting tables
- Complete test setup

**Files:**
- `metadata.json` - Component configuration
- `fullrun.sql` - Execution logic
- `dryrun.sql` - Schema preview logic
- `test/test.json` - Test configuration
- `test/input_data.ndjson` - Test data
- `test/fixtures/1.json` - Expected output

**Use case:** Start here if you're creating your first component.

---

## 02-multi-input-component

**Purpose:** Shows how to use different input types in a single component.

**What it demonstrates:**
- Table and Column inputs
- String and Number inputs
- Boolean and Selection inputs
- Range input
- Optional vs required inputs
- Default values
- Helper text

**Files:**
- `metadata.json` - Component configuration with 8 different input types

**Use case:** Reference when adding various input types to your component.

---

## 03-conditional-inputs

**Purpose:** Shows dynamic UI behavior based on user selections.

**What it demonstrates:**
- `showIf` conditional visibility
- Multiple conditions
- Cascading selections
- Advanced options grouping

**Files:**
- `metadata.json` - Component configuration with conditional inputs

**Use case:** When you need inputs to appear/hide based on other selections.

---

## How to Use These Examples

### For Learning
1. Start with `01-minimal-component` - read all files to understand structure
2. Review `02-multi-input-component` to see input type variety
3. Study `03-conditional-inputs` for advanced UI patterns

### For Building
1. Copy relevant example as starting point
2. Modify metadata to match your needs
3. Implement SQL logic (see `01-minimal-component` for pattern)
4. Add tests (see `01-minimal-component/test/`)
5. Deploy and test: `python carto_extension.py deploy --destination=...`

### For Reference
- **"What input type should I use?"** → See `02-multi-input-component`
- **"How do I make inputs conditional?"** → See `03-conditional-inputs`
- **"How do I structure tests?"** → See `01-minimal-component/test/`
- **"What SQL patterns work?"** → See `01-minimal-component/*.sql`

---

## Testing These Examples

These examples are pedagogical - they're designed for learning, not for direct deployment to production. However, `01-minimal-component` is fully functional:

```bash
# Copy to your extension's components folder
cp -r doc/examples/01-minimal-component components/example_component

# Update your root metadata.json to include it
# Add "example_component" to the components array

# Deploy
python carto_extension.py deploy --destination=yourproject.yourdataset

# Test in Workflows UI
```

---

## Related Documentation

- [Component Metadata Reference](../component_metadata.md) - Complete input type reference
- [Writing Stored Procedures](../procedure.md) - SQL patterns and best practices
- [Running Tests](../running_tests.md) - Testing guide
- [Quickstart](../quickstart.md) - Build your first component in 5 minutes
- [Validation Rules](../reference/validation-rules.md) - All constraints and rules

---

## Contributing Examples

If you develop a useful pattern not covered here, consider contributing it back! Examples should be:
- **Minimal:** Only what's needed to demonstrate the pattern
- **Pedagogical:** Focused on teaching, not production use
- **Documented:** Heavy inline comments explaining decisions
- **Complete:** If showing SQL, include both fullrun and dryrun
