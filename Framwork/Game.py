# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

import sys
from pathlib import Path

# Add the project root (two directories above this file) to Python's import path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game_pages.main_app import App

# ---------- Run ----------
if __name__ == '__main__':
    app = App()
    app.toggle_fullscreen()
    app.mainloop()
