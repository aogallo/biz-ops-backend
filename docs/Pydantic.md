# Pydantic

## Models

One of the primary ways of defining schema in Pydantic is via models. Models are simple classes
which inherit from BaseModel and define fields as annotated attributes.

### Basic model usage

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
  id: int
  name: str = 'Jane Doe'

  model_config = ConfigDict(str_max_length=10)
```

In this example, `User` is a model with two fields:

- id, which is an integer and is required.
- name, which is a string and is not required (it has a default value).

Fields can be customized in a number of ways using the [`Field()`](#fields) function.

The model instance can be serialized using the `model_dump()` method:

```python
assert user.model_dump() == { 'id': 123, 'name': 'Jane Doe' }
```

### Model methods and properties

- `model_validate()`: Validates the given object against the Pydantic model.
- `model_validate_json()`: Validates the given JSON data against the Pydantic model.
- `model_construct()`: Creates models without running validation.
- `model_dump()`: Returns a dictionary of the model's fields and values.
- `model_dump_json()`: Returns a JSON string representation of `model_dump()`.
- `model_copy()`: Returns a copy (by default, shallow copy) of the model.
- `model_json_schema()`: Returns a jsonable dictionary representation the model's JSON Schema.
- `model_fields()`: A mapping between field names and their definitions (FieldInfo instances).
- `model_computed_fields()`: A mapping between computed field names and their definitions (ComputedFieldInfo instances).
- `model_extra()`: The extra fields set during validation.
- `model_fields_set()`: The set of fields which were explicitly provided when the model was initialized.

More information [Models - Model Methods](https://docs.pydantic.dev/latest/concepts/models/#model-methods-and-properties)

## Fields
