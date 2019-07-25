import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='autodesk',
    description='Automatic standing desk controller.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.0',
    author='Daniel Oom',
    author_email='oom.daniel@gmail.com',
    url='https://github.com/daoo/autodesk',
    packages=setuptools.find_packages(),
    package_data={
        'autodesk': [
            'templates/*.*'
        ]
    },
    include_package_data=True,
    install_requires=[
        'aiohttp>=3.5.4, <3.6',
        'aiohttp_jinja2>=1.1.2, <1.2',
        'matplotlib>=3.1.1, <3.2',
        'numpy>=1.16.4, <1.17',
        'pandas>=0.25, <0.26',
        'pyyaml>=5.1.1, <5.2'
    ],
)
