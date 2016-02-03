#!/usr/bin/env python

# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the author be held liable for any damages
# arising from the use of this software.
# 
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
# 
# Copyright (c) 2008 Greg Hewgill http://hewgill.com
#
# This has been modified from the original software.
# Copyright (c) 2011,2012 Scott Kitterman <scott@kitterman.com>

from distutils.core import setup
import os

version = "0.5.6"

setup(
    name = "dkimpy",
    version = version,
    description = "DKIM (DomainKeys Identified Mail)",
    long_description =
    """dkimpy is a Python library that implements DKIM (DomainKeys
Identified Mail) email signing and verification.""",
    author = "Scott Kitterman",
    author_email = "scott@kitterman.com",
    url = "https://launchpad.net/dkimpy",
    license = "BSD-like",
    packages = ["dkim"],
    scripts = ["dkimsign.py", "dkimverify.py"],
    data_files = [(os.path.join('share', 'man', 'man1'),
        ['man/dkimsign.1']), (os.path.join('share', 'man', 'man1'),
        ['man/dkimverify.1'])],
    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Environment :: No Input/Output (Daemon)',
      'Intended Audience :: Developers',
      'License :: DFSG approved',
      'Natural Language :: English',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Communications :: Email :: Mail Transport Agents',
      'Topic :: Communications :: Email :: Filters',
      'Topic :: Internet :: Name Service (DNS)',
      'Topic :: Software Development :: Libraries :: Python Modules'
      ]
)

if os.name != 'posix':
    data_files = ''
