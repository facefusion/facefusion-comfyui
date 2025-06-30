from typing import Any, Dict, Literal, TypeAlias

NodeInputTypes : TypeAlias = Dict[str, Any]
NodeClassMapping : TypeAlias = Dict[str, Any]
NodeDisplayNameMapping : TypeAlias = Dict[str, str]

Image : TypeAlias = Any

FaceSwapperModel = Literal['hyperswap_1a_256', 'hyperswap_1b_256', 'hyperswap_1c_256']
