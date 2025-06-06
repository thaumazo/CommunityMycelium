import json
from types import FunctionType


class UniversalEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            # If the object has a __dict__, return it (excluding callables and private attrs)
            if hasattr(obj, "__dict__"):
                return {
                    k: v
                    for k, v in vars(obj).items()
                    if not k.startswith("_") and not isinstance(v, FunctionType)
                }
            # If the object is iterable but not a string
            elif hasattr(obj, "__iter__") and not isinstance(obj, str):
                return list(obj)
            else:
                return str(obj)  # Fallback for unhandled types
        except Exception as e:
            return f"<Unserializable object: {e}>"


def dump(obj, pretty=False):
    try:
        if pretty:
            return json.dumps(obj, cls=UniversalEncoder, indent=2)
        return json.dumps(obj, cls=UniversalEncoder)
    except Exception as e:
        return f"Failed to dump object: {e}"
