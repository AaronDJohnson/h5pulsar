# pulsar.py
"""Class containing pulsar data from timing package [tempo2/PINT].
"""

import contextlib
import json
import logging
import os
import pickle
from io import StringIO
from typing import Optional

import astropy.constants as const
import astropy.units as u
import numpy as np
from ephem import Ecliptic, Equatorial

import enterprise
from enterprise.signals import utils
from enterprise.pulsar_inflate import PulsarInflater

from h5pulsar.h5format import H5Format
from h5pulsar import derivative_file

logger = logging.getLogger(__name__)


class BaseHdf5Pulsar(enterprise.pulsar.BasePulsar):
    """Base class that implements the to_hdf5 functionality"""

    def to_hdf5(self, h5path, fmt=None):
        """Save this object to an HDF5 format."""

        if fmt is None:
            fmt = derivative_file.derivative_format()
        # Save MJDI, MJDF to retain full accuracy without longdouble
        # FIXME: can T2Pulsar provide this?
        if hasattr(self, "pint_toas"):
            logger.info("Creating MJDI/MJDF parameters")
            tdbs = [t.tdb for t in self.pint_toas["mjd"]]
            jd1, jd2 = np.array([(t.jd1, t.jd2) for t in tdbs]).T
            mjd1 = jd1 - 2400000
            mjd2 = jd2 - 0.5
            mjd1 += mjd2 // 1
            mjd2 = mjd2 % 1
            self.mjdi = mjd1.astype(np.int64)
            self.mjdf = mjd2
        fmt.save_to_hdf5(h5path, self)
        # FIXME: try/finally to remove mjdi/mjdf?


class PintPulsar(enterprise.pulsar.PintPulsar, BaseHdf5Pulsar):

    def __init__(self, toas, model, sort=True, drop_pintpsr=True, planets=True):

        super().__init__(toas, model, sort=sort, drop_pintpsr=drop_pintpsr, planets=planets)


class Tempo2Pulsar(enterprise.pulsar.Tempo2Pulsar, BaseHdf5Pulsar):

    def __init__(
        self,
        t2pulsar,
        sort=True,
        drop_t2pulsar=True,
        planets=True,
        par_name=None,
        tim_name=None,
    ):

        super().__init__(t2pulsar, sort=sort, drop_t2pulsar=drop_t2pulsar, planets=planets, par_name=par_name, tim_name=tim_name)


# FIXME: format version?
# Current format version could be set in this file
# Reading a file with a version that might not be compatible should emit a warning
class FilePulsar(BaseHdf5Pulsar):
    """A Pulsar object created from the data in an HDF5 file."""

    def __init__(self, h5path, sort=True, planets=True, fmt: Optional[H5Format] = None):
        """Build a FilePulsar from an HDF5 file."""
        if fmt is None:
            fmt = derivative_file.derivative_format()
        fmt.load_from_hdf5(h5path, self)
        self._sort = sort
        self.sort_data()
        self.planets = planets


def Pulsar(*args, **kwargs):
    ephem = kwargs.get("ephem")
    clk = kwargs.get("clk")
    bipm_version = kwargs.get("bipm_version")
    planets = kwargs.get("planets", True)
    sort = kwargs.get("sort", True)
    drop_t2pulsar = kwargs.get("drop_t2pulsar", True)
    drop_pintpsr = kwargs.get("drop_pintpsr", True)
    timing_package = kwargs.get("timing_package")
    if timing_package is not None:
        timing_package = timing_package.lower()

    if pint is not None:
        toas = [x for x in args if isinstance(x, TOAs)]
        model = [x for x in args if isinstance(x, TimingModel)]

    if t2 is not None:
        t2pulsar = [x for x in args if isinstance(x, t2.tempopulsar)]

    parfile = [x for x in args if isinstance(x, str) and x.split(".")[-1] == "par"]
    timfile = [x for x in args if isinstance(x, str) and x.split(".")[-1] in ["tim", "toa"]]

    if pint and toas and model:
        return PintPulsar(toas[0], model[0], sort=sort, drop_pintpsr=drop_pintpsr, planets=planets)
    elif t2 and t2pulsar:
        return Tempo2Pulsar(t2pulsar[0], sort=sort, drop_t2pulsar=drop_t2pulsar, planets=planets)
    elif parfile and timfile:
        # Check whether the two files exist
        if not os.path.isfile(parfile[0]) or not os.path.isfile(timfile[0]):
            msg = "Cannot find parfile {0} or timfile {1}!".format(parfile[0], timfile[0])
            raise IOError(msg)

        # Obtain the directory name of the timfile, and change to it
        timfiletup = os.path.split(timfile[0])
        dirname = timfiletup[0] or "./"
        reltimfile = timfiletup[-1]
        relparfile = os.path.relpath(parfile[0], dirname)

        if timing_package is None:
            if t2 is not None:
                timing_package = "tempo2"
            elif pint is not None:
                timing_package = "pint"
            else:
                raise ValueError("No timing package available with which to load a pulsar")

        # get current directory
        cwd = os.getcwd()
        try:
            # Change directory to the base directory of the tim-file to deal with
            # INCLUDE statements in the tim-file
            os.chdir(dirname)
            if timing_package.lower == "tempo2":
                if t2 is None:
                    raise ValueError("tempo2 requested but tempo2 is not available")
                # hack to set maxobs
                maxobs = get_maxobs(reltimfile) + 100
                t2pulsar = t2.tempopulsar(relparfile, reltimfile, maxobs=maxobs, ephem=ephem, clk=clk)
                return Tempo2Pulsar(
                    t2pulsar,
                    sort=sort,
                    drop_t2pulsar=drop_t2pulsar,
                    planets=planets,
                    par_name=relparfile,
                    tim_name=reltimfile,
                )
            elif timing_package.lower() == "pint":
                if pint is None:
                    raise ValueError("PINT requested but PINT is not available")
                if (clk is not None) and (bipm_version is None):
                    bipm_version = clk.split("(")[1][:-1]
                model, toas = get_model_and_toas(
                    relparfile, reltimfile, ephem=ephem, bipm_version=bipm_version, planets=planets
                )
                os.chdir(cwd)
                return PintPulsar(toas, model, sort=sort, drop_pintpsr=drop_pintpsr, planets=planets)
            else:
                raise ValueError(f"Unknown timing package {timing_package}")
        finally:
            os.chdir(cwd)
    raise ValueError("Pulsar (par/tim) not specified in {args} or {kwargs}")
