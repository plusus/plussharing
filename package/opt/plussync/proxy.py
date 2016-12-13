class Proxy:
    """
    Delegate method calls to some implementation
    """
    def __init__(self, delegate):
        super().__init__()
        self._delegate = delegate

    def __getattr__(self, name):
        return getattr(self._delegate, name)

    def update_delegate(self, delegate):
        self._delegate = delegate

    def delegate(self):
        return self._delegate