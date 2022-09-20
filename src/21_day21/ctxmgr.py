from ansa import base


class MyImportV1:
    def __init__(self):
        self.a = base.ImportV1()

    @property
    def _attrs(self):
        return ('nodes',
                'shells',
                'solids')

    def __enter__(self):
        self.a.start()
        return self.a

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.a.build()
        for _attr in self._attrs:
            attr = getattr(self.a, _attr)
            setattr(self, _attr, attr)
        self.a.finish()
