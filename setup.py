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
        'aiohttp>=3.8.1, <3.9',
        'aiohttp_jinja2>=1.5, <1.6',
        'matplotlib>=3.5.1, <3.6',
        'numpy>=1.22.3, <1.23',
        'pandas>=1.4.2, <1.5',
        'pyyaml>=6.0, <6.1',
        'pyftdi>=0.54, <0.55',
    ],
)
