# Documentation Index

Welcome to the Business Operations Backend documentation! This folder contains guides and references to help you develop features efficiently.

## 📖 Available Documentation

### For Developers

#### [Quick Reference](QUICK_REFERENCE.md) 🚀
**Start here if you need to create a new API endpoint quickly**

- File templates ready to copy-paste
- Common patterns and examples
- Quick troubleshooting for common mistakes
- Type hints cheatsheet
- Best for: Experienced developers who need a quick reminder

#### [API Schema & Entity Development Guide](API_SCHEMA_ENTITY_GUIDE.md) 📚
**Read this for comprehensive understanding**

- Complete architecture overview
- Step-by-step tutorial for creating endpoints
- Detailed explanation of camelCase conversion
- Understanding `model_dump()` and `model_validate()`
- Validation error handling
- Complete worked examples
- Best for: New team members or when learning the architecture

## 🎯 When to Use Which Guide

| Situation | Recommended Guide |
|-----------|------------------|
| Creating a new API endpoint | [Quick Reference](QUICK_REFERENCE.md) |
| Understanding the architecture | [Complete Guide](API_SCHEMA_ENTITY_GUIDE.md) |
| Debugging validation errors | [Complete Guide](API_SCHEMA_ENTITY_GUIDE.md) - Validation section |
| Quick syntax lookup | [Quick Reference](QUICK_REFERENCE.md) |
| Onboarding new developers | [Complete Guide](API_SCHEMA_ENTITY_GUIDE.md) |
| Understanding `model_dump()` | [Complete Guide](API_SCHEMA_ENTITY_GUIDE.md) - Understanding section |

## 🏗️ Architecture Overview

Our backend follows a layered architecture:

```
┌─────────────────────────────────────────┐
│  Routes (API Layer)                     │  ← Uses Schemas (camelCase)
│  app/routes/                            │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Services (Business Logic)              │  ← Uses Entities (snake_case)
│  app/services/                          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Repositories (Data Access)             │  ← Uses Entities (snake_case)
│  app/infrastructure/repositories/       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Database (PostgreSQL)                  │  ← Stores in snake_case
└─────────────────────────────────────────┘
```

## 🔑 Key Concepts

### Schemas vs Entities

- **Schemas** (`app/schemas/`): API layer, handles camelCase ↔ snake_case conversion
- **Entities** (`app/domain/entities/`): Domain layer, uses pure snake_case

### CamelCase Conversion

Frontend sends/receives camelCase, backend uses snake_case internally:

```
Frontend: {"phoneNumber": "555-0100"}
    ↓ (CamelCaseSchema)
Backend: phone_number = "555-0100"
    ↓ (CamelCaseSchema)
Frontend: {"phoneNumber": "555-0100"}
```

### The Two Essential Methods

1. **`model_dump()`** - Converts Pydantic model → dictionary
2. **`model_validate()`** - Converts entity → Pydantic schema

## 📋 Quick Start

1. Read the [Quick Reference](QUICK_REFERENCE.md)
2. Copy the appropriate template
3. Replace `Resource` with your actual resource name
4. Follow the checklist
5. Test your endpoint

## 🔍 Working Examples

Check these files in the codebase for reference:

- **Product**: Well-structured example with all layers
  - `app/domain/entities/product.py`
  - `app/schemas/product_schema.py`
  - `app/services/product_service.py`
  - `app/routes/product_routes.py`

- **Account**: Recently refactored example following best practices
  - `app/domain/entities/account.py`
  - `app/schemas/account_schema.py`
  - `app/services/account_service.py`
  - `app/routes/account_routes.py`

## 🤝 Contributing to Documentation

Found something unclear? Have suggestions?

1. Update the relevant documentation file
2. Follow the same structure and formatting
3. Add examples when possible
4. Keep it concise and actionable

## 📞 Need Help?

1. Check the [Quick Reference](QUICK_REFERENCE.md) for syntax
2. Read the [Complete Guide](API_SCHEMA_ENTITY_GUIDE.md) for concepts
3. Review working examples in the codebase
4. Ask the team!

---

**Happy coding! 🚀**
