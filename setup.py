from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="h5pulsar",
    version="1.1.0",
    author="Rutger van Haasteren",
    author_email="rutger@vhaasteren.com",
    description="HDF5 read/write capabilities for Enterprise Pulsar objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vhaasteren/h5pulsar",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.16.3",
        "astropy>=4.0,!=4.0.1,!=4.0.1.post1",
        "enterprise-pulsar>=3.3.4",
        "jplephem>=2.6",
        "h5py>=3.9.0",
    ],
)
