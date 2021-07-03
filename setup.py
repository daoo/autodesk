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
        'aiohttp>=3.7.3, <3.8',
        'aiohttp_jinja2>=1.4.2, <1.5',
        'matplotlib>=3.4.2, <3.5',
        'numpy>=1.21.0, <1.22',
        'pandas>=1.2.5, <1.3',
        'pyyaml>=5.4.1, <5.5',
        'pyftdi>=0.53.1, <0.54',
    ],
)
