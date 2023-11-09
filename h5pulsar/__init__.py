from .h5pulsar import PintPulsar, Tempo2Pulsar, Pulsar, FilePulsar, BasePulsar

try:
    from ._version import __version__
except ImportError:
    # _version.py will be missing during package setup when setuptools_scm has not yet written it
    __version__ = "unknown"
