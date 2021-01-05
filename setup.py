##############################################################################
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import sys

py_version = sys.version_info[:2]

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md')).read()
except (IOError, OSError):
    README = ''
try:
    CHANGES = open(os.path.join(here, 'CHANGES.md')).read()
except (IOError, OSError):
    CHANGES = ''

setup(name='superhooks-discord',
      version='0.1',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      description='superhooks-discord plugin for supervisord',
      long_description=README + '\n\n' + CHANGES,
      long_description_content_type='text/markdown',
      classifiers=[
          "Development Status :: 3 - Alpha",
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: System :: Boot',
          'Topic :: System :: Monitoring',
          'Topic :: System :: Systems Administration',
      ],
      author='Sean Breckenridge',
      author_email='seanbrecke@gmail.com',
      url="https://github.com/seanbrecke/superhooks",
      keywords='supervisor web hooks monitoring discord',
      packages=find_packages(include=["superhooks_discord"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'superlance',
          'supervisor',
          'requests',
      ],
      entry_points="""\
      [console_scripts]
      superhooks-discord = superhooks_discord.superhooks:main
      """
      )
