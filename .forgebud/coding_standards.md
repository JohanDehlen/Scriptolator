# Coding Standards

## General Principles

- Prefer readable code over clever code.
- Keep responsibilities clearly separated.
- Preserve existing functionality unless a change is intentional.
- Avoid duplicated logic.
- Keep implementations simple and explicit.

## Language and Framework Conventions

Document the language, framework, and library conventions used by
this project.

## Naming

- Use descriptive names.
- Follow the naming conventions of the project's language.
- Avoid unclear abbreviations.

## Type Hints

- Add type hints where supported and practical.
- Keep public interfaces explicit.
- Avoid ambiguous return types.

## Functions and Classes

- Give each function and class one clear responsibility.
- Keep methods focused and reasonably short.
- Prefer composition over inheritance.
- Avoid hidden side effects.

## Error Handling

- Handle expected failures explicitly.
- Do not silently ignore important errors.
- Provide useful error messages.
- Avoid broad exception handling unless recovery is intentional.

## Documentation

- Write meaningful docstrings for public classes and methods.
- Explain why a non-obvious decision was made.
- Keep documentation synchronized with implementation.

## Testing

- Add tests for new behavior where practical.
- Preserve existing tests.
- Test failure paths as well as successful paths.

## Dependencies

- Reuse existing dependencies when appropriate.
- Avoid adding unnecessary packages.
- Record significant dependency decisions in project memory.

## Project-Specific Rules

Add project-specific coding rules below this section.
