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
        'aiohttp>=3.6.2, <3.7',
        'aiohttp_jinja2>=1.2.0, <1.3',
        'matplotlib>=3.2.1, <3.3',
        'numpy>=1.18.2, <1.19',
        'pandas>=1.0.3, <1.1',
        'pyyaml>=5.3.1, <5.4',
        'pyftdi>=0.50, <0.51',
    ],
)
