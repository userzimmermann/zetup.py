
import sys

from zetup.config import load_zetup_config


load_zetup_config(__path__[0], sys.modules[__name__])
