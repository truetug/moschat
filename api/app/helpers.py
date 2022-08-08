import importlib
import json

import pydantic.json



def import_class(path: str):
    path, cls_name = path.rsplit(".", 1)
    module = importlib.import_module(path)
    cls = getattr(module, cls_name)
    return cls


def _custom_json_serializer(*args, **kwargs) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs)
