import sys

from base import ctx
from combiner import Combiner

if __name__ == "__main__":
    # might want to set an exception hook to messagebox errors... e.g. sys.excepthook = excepthook
    app = Combiner(ctx)
    exit_code = app.run()
    sys.exit(exit_code)
