import os
from setuptools import setup, find_packages

with open('requirements.txt') as file_requirements:
    requirements = file_requirements.read().splitlines()

setup(
    name='ebsrs',
    version='0.1.0',
    author='John Paul P. Doria',
    author_email='jp@lazyadm.in',
    description=('Restore snapshots created by ebs-snapshot-python ' +
                 '(https://github.com/jpdoria/ebs-snapshot-python.'),
    license='MIT',
    keywords='aws ec2 ebs restore snapshot',
    url='https://github.com/jpdoria/ebsrs',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ebsrs = ebsrs.ebsrs:main'
        ]
    },
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
)
