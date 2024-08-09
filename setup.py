import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autodesk",
    description="Automatic standing desk controller.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.0",
    author="Daniel Oom",
    author_email="oom.daniel@gmail.com",
    url="https://github.com/daoo/autodesk",
    packages=setuptools.find_packages(),
    package_data={"autodesk": ["templates/*.*"]},
    include_package_data=True,
    install_requires=[
        "aiohttp==3.10.2",
        "aiohttp-jinja2==1.6",
        "matplotlib==3.9.0",
        "numpy==1.26.4",
        "pandas==2.2.2",
        "pyyaml==6.0.1",
        "pyftdi==0.55.4",
    ],
)
