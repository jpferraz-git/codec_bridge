from setuptools import setup, find_packages

setup(
    name='codec_bridge',
    version='0.2.4',
    packages=find_packages(),
    description='Encoding and case normalization bridge for DuckDB and other engines',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='João Pedro Ferraz Bezerra',
    author_email='jpferraz554@gmail.com',
    url='https://github.com/jpferraz-git/codec_bridge',
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.11',
)