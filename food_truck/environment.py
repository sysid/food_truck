import logging
import os
import sys
from pathlib import Path
from typing import Union, Optional, Any, Dict

from pydantic import BaseSettings
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker

_log = logging.getLogger(__name__)

env_file_sentinel = str(object())

run_env = os.environ.get("RUN_ENV", None)
if not run_env:
    print("No run_env specified. Exiting.")
    sys.exit()
run_env = run_env.lower()

ROOT_DIR = Path(__file__).parent.parent.absolute()
env_path = ROOT_DIR / f".env.{run_env}"
if not Path(env_path).is_file():
    print(f"No env file '{env_path}' found for environment. Exiting.")
    sys.exit()


class Environment(BaseSettings):
    run_env: str
    log_level: str = "INFO"

    # alpha_vantage_apikey: str = "6VBKDJ81BDRGDY68"
    alpha_vantage_apikey: str = "xxxxxxxxx"
    alpha_vantage_url: str = "https://www.alphavantage.co"

    def __init__(
        self,
        _env_file: Union[Path, str, None] = env_file_sentinel,
        _env_file_encoding: Optional[str] = None,
        **values: Any,
    ):
        super().__init__(
            _env_file=_env_file, _env_file_encoding=_env_file_encoding, **values
        )

    def log_config(self) -> Dict:
        cfg = self.dict()
        skip_keys = ("api_key",)
        sanitized_cfg = {k: v for k, v in cfg.items() if k not in skip_keys}
        return sanitized_cfg


config = Environment(_env_file=env_path)
