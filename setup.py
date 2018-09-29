import ast
import re

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('xweb.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
            f.read().decode('utf-8')).group(1)))

setup(name='xweb',
      version=version,
      description='High performance web framework built with uvloop and httptools.',
      author='gaojiuli',
      long_description=open('README.md', 'r', encoding='utf8').read(),
      long_description_content_type='text/markdown',
      author_email='gaojiuli@gmail.com',
      url='https://github.com/gaojiuli/xweb',
      py_modules=['xweb'],
      install_requires=[
          'asyncio',
          'ujson',
          'uvloop',
          'httptools',
          'gunicorn'
      ],
      license='MIT',
      platforms='any',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
                   'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                   'Topic :: Software Development :: Libraries :: Application Frameworks',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   ],
      )
