
import sys

from base import ctx
from combiner import Combiner

if __name__ == '__main__':
    app = Combiner(ctx)
    exit_code = app.run()
    sys.exit(exit_code)
