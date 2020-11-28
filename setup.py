from distutils.core import setup
from os import path

from dblstats.version import version

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dblstats',
    packages=['dblstats', 'dblstats.objects', 'dblstats.utils'],
    version=version,
    license='MIT',
    description='A python dblstats.com API wrapper.',
    # project_urls={
    #     "Documentation": "WIP",
    # },
    long_description=long_description,
    author='Arthurdw',
    author_email='mail.arthurdw@gmail.com',
    url='https://github.com/Arthurdw/dblstats',
    download_url=f'https://github.com/Arthurdw/dblstats/archive/{version}.tar.gz',
    keywords=["dbl", "stats", "statistics", "dblstatistics.com"],
    install_requires=[
        "aiohttp"
    ],
    classifiers=[
        # 'Development Status :: 2 - Pre-Alpha',
        # Development statuses:
        # Development Status :: 1 - Planning
        # Development Status :: 2 - Pre-Alpha
        # Development Status :: 3 - Alpha
        'Development Status :: 4 - Beta',
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
