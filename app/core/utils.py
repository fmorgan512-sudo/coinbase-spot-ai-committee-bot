import json
import time


def now_ts() -> int:
      return int(time.time())


def dumps(obj) -> str:
      return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=str)
