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
        'matplotlib>=3.3.3, <3.4',
        'numpy>=1.19.4, <1.20',
        'pandas>=1.1.5, <1.2',
        'pyyaml>=5.3.1, <5.4',
        'pyftdi>=0.52, <0.53',
    ],
)
