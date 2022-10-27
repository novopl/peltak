import dataclasses
from typing import Any, Dict, Optional, Tuple


@dataclasses.dataclass
class ExcValues:
    args: Tuple
    kwargs: Dict[str, Any]


class PeltakError(Exception):
    msg: str = "peltak error"

    def __init__(
        self,
        detail: Optional[str] = None,
        *args,
        **kw
    ):
        message = self.msg.format(*args, **kw) + (f": {detail}" if detail else '')
        super(PeltakError, self).__init__(message)

        self.detail = detail
        # self.args is already used by Exception
        self.values = ExcValues(args, kw)
