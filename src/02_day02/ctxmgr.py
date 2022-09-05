class CtxMgr:
    def __init__(self, a):
        '''
        Do some init if needed
        '''
        self.a = a

    def hello(self):
        print('Hello !')

    def __enter__(self):
        print('__enter__ called')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        print('__exit__ called')
        del self.a


def main():
    with CtxMgr('a') as ctxmgr:
        ctxmgr.hello()
        print(f'{ctxmgr.a=}')  # get 'a' back

    # will raise AttributeError if called outside with
    print(ctxmgr.a)


if __name__ == '__main__':
    main()
