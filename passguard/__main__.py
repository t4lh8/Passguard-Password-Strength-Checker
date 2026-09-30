import os
import sys

from .cli import main

if os.name == "nt":
    os.system("")  # enables ANSI colors in the Windows console

sys.exit(main())
