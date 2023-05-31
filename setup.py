from setuptools import setup

setup(
    name='h5pulsar',
    version='1.0.0',
    author='Anne Archibald',
    description='Use h5py to read ENTERPRISE Pulsar objects',
    packages=['h5pulsar'],
    entry_points={
        'console_scripts': [
            'my_program = my_program.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)