## v0.7.0 (2025-02-09)

### Fix

- **fields**: fixed inconsistent behaviour on fields filter
- **fields/conditions**: gave fields a parent property, allowing recursive and nested conditional queries
- **results-select**: fixed resutlts select to prefer to return the corrent type (list or single value) - only locally accurate
- **results**: upgraded dw for a datetime issue in V1; added custom exception for conversion errors
- **offset-pagination**: fixed offset pagination to work on single results
- **fields**: greatly simplified field definition on models; made to_model return list always

## v0.6.0 (2025-02-07)

### Feat

- **results**: result class now has a variety of filtering options
- **responses**: added model_request to clients that wraps all results in a Results object
- **project**: upgraded python to 3.12; swapped to implicit future annotations

### Refactor

- **models**: moved models into a submodule
- added del handler to base client
- changed all httpx imports to be just base package
- more consistent typing in models and pagination
- **auth**: moved authentication into a subdirectory

## v0.5.0 (2025-02-03)

### Feat

- **pagination**: async finalized

## v0.4.0 (2025-02-03)

### Feat

- **pagination**: async finalized

## v0.3.0 (2025-02-02)

### Feat

- **project**: added async functionality - required global rework
- added abstract pagination

### Fix

- **project**: added mypy; conform to mypy; downgraded dw

## v0.2.0 (2025-02-02)

### Feat

- **Project**: added core logic and interactions for clients, auth, and models

## v0.1.0 (2025-02-02)
