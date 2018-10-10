from typing import Optional, List, Mapping
import logging
import shutil
import multiprocessing
from multiprocessing.pool import ThreadPool
import subprocess as sub
import os
import sys
import re
import pandas as pd
from .input import Input
from .beam import Beam
from .output import read_plt_file


def find_labeled_output(out, label):
    data = []
    for l in out:
        if str(label) in l and 'Keyword' in l:
            data.append(l)
            continue
        if len(data) > 0:
            if '****' in l:
                break
            data.append(l)
    return list(filter(lambda _: len(_), data))


class ZgoubiException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class ZgoubiRun:
    def __init__(self, results: List[Mapping]):
        self._results = results
        self._tracks = None

    @property
    def tracks(self):
        if self._tracks is None:
            try:
                tracks = list()
                for r in self._results:
                    tracks.append(read_plt_file(path=r['path']))
                self._tracks = pd.concat(tracks)
            except FileNotFoundError:
                logging.getLogger(__name__).warning(
                    "Unable to read and load the Zgoubi .plt files required to collect the tracks.")
                return None
        return self._tracks

    @property
    def matrix(self):
        pass

    @property
    def results(self):
        return self._results


class Zgoubi:
    """Encapsulation of methods to run Zgoubi from Python."""
    ZGOUBI_RES_FILE = 'zgoubi.res'

    def __init__(self, executable='zgoubi', path=None):
        """

        :param beamlines:
        :param path: path to the simulator executable (default: lookup using 'which')
        :param kwargs:
        """
        self._executable: str = executable
        self._path: str = path
        self._results: List[multiprocessing.pool.ApplyResult] = list()

    @property
    def executable(self) -> str:
        """

        :return:
        """
        return self._get_exec()

    def __call__(self, _: Input, beam: Optional[Beam]=None, debug=False, n_procs=None):
        """

        :param _:
        :param beam:
        :param debug:
        :return:
        """
        n = n_procs or multiprocessing.cpu_count()
        paths = _(beam)
        self._results = list()
        pool = ThreadPool(n)
        for p in paths:
            try:
                path = p.name
            except AttributeError:
                path = p
            self._results.append(pool.apply_async(self._execute_zgoubi, (_, path)))
        pool.close()
        pool.join()
        return ZgoubiRun(list(map(lambda _: getattr(_, 'get', None)(), self._results)))

    def _execute_zgoubi(self, _: Input, path: str='.', debug=False) -> dict:
        """

        :param _:
        :param path:
        :param debug:
        :return: a dictionary holding the results of the run
        """
        stderr = None
        p = sub.Popen([self._get_exec()],
                      stdin=sub.PIPE,
                      stdout=sub.PIPE,
                      stderr=sub.STDOUT,
                      cwd=path,
                      shell=False,
                      )

        # Run
        output = p.communicate()

        # Collect STDERR
        if output[1] is not None:
            stderr = output[1].decode()

        # Extract element by element output
        result = open(os.path.join(path, Zgoubi.ZGOUBI_RES_FILE), 'r').read().split('\n')
        for e in _.line:
            list(map(e.attach_output, find_labeled_output(result, e.LABEL1)))

        # Extract CPU time
        cputime = -1.0
        if stderr is None:
            lines = [line.strip() for line in output[0].decode().split('\n') if
                     re.search('CPU time', line)]
            if len(lines):
                cputime = float(re.search("\d+\.\d+[E|e]?[+|-]?\d+", lines[0]).group())
        if debug:
            print(output[0].decode())
        try:
            return {
                'stdout': output[0].decode().split('\n'),
                'stderr': stderr,
                'cputime': cputime,
                'result': result,
                'input': _,
                'path': path,
            }
        except FileNotFoundError:
            raise ZgoubiException("Executation terminated with errors.")

    def _get_exec(self, optional_path: str='/usr/local/bin') -> str:
        """Retrive the path to the Zgoubi executable."""
        if self._path is not None:
            return os.path.join(self._path, self._executable)
        elif sys.platform in ('win32', 'win64'):
            return shutil.which(self._executable)
        else:
            if os.path.isfile(f"{sys.prefix}/bin/{self._executable}"):
                return f"{sys.prefix}/bin/{self._executable}"
            else:
                return shutil.which(self._executable, path=os.path.join(os.environ['PATH'], optional_path))

