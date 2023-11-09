from setuptools import setup, find_packages

setup(
    name="h5pulsar",
    use_scm_version={
        "write_to": "h5pulsar/_version.py",
        "write_to_template": "__version__ = '{version}'",
    },
    author="Rutger van Haasteren",
    author_email="rutger@vhaasteren.com",
    packages=find_packages(),
    url="http://github.com/vhaasteren/h5pulsar/",
    description="HDF5 read/write capabilities for Enterprise Pulsar objects",
    license="MIT",
    long_description=open("README.md").read(),
    url="https://github.com/vhaasteren/h5pulsar",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    python_requires=">=3.9",
)
