import sys

from base import ctx
from combiner import Combiner
from excepthook import excepthook

if __name__ == "__main__":

    # Install global exception hook
    sys._excepthook = sys.excepthook
    sys.excepthook = excepthook

    app = Combiner(ctx)
    exit_code = app.run()
    sys.excepthook = excepthook
    sys.exit(exit_code)
