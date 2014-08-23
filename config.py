from path import path as Path


ZETUP_DIR = '.'
exec((Path(__file__).dirname() / 'zetup.py').text())
