"""Patchable elements module."""
from typing import Optional
import pandas as _pd
from .. import ureg as _ureg
from .. import Q_ as _Q
from georges_core.frame import Frame as _Frame


class Patchable:
    """Patchable elements are Zgoubi commands that affect the placement of the reference frame.

    A default implementation of the placement methods is provided for subclasses. It only places the entrance frame
    at the location of the placement frame and all other frames are set to the entrance frame ('point-like' element).
    """

    def __init__(self):
        """Initializes a un-patched patchable element."""
        self.LABEL1 = None
        self._entry: Optional[_Frame] = None
        self._entry_patched: Optional[_Frame] = None
        self._exit: Optional[_Frame] = None
        self._exit_patched: Optional[_Frame] = None
        self._frenet: Optional[_Frame] = None
        self._center: Optional[_Frame] = None
        self._reference_trajectory: Optional[_pd.DataFrame] = None

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = t['X'] + self.entry_s.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y']
        try:
            tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo']
        except KeyError:
            pass
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        try:
            tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        except KeyError:
            pass

    def place(self, frame: _Frame):
        """Place the element with a reference frame.

        All the frames of the element are reset and the entrance frame is then placed with respect to the reference
        frame.

        Args:
            frame: the reference frame for the placement of the entrance frame.
        """
        self.clear_placement()
        self._entry = frame.__class__(frame)

    def clear_placement(self):
        """Clears all the frames."""
        self._entry = None
        self._entry_patched = None
        self._exit = None
        self._exit_patched = None
        self._center = None

    @property
    def length(self) -> _Q:
        """Length of the element.

        Returns:
            the length of the element with units.
        """
        return 0.0 * _ureg.cm

    @property
    def entry(self) -> Optional[_Frame]:
        """Entrance frame.

        Returns:
            the frame of the entrance of the element.
        """
        return self._entry

    @property
    def entry_patched(self) -> Optional[_Frame]:
        """Entrance patched frame.

        Returns:
            the frame of the entrance of the element with the patch applied.
        """
        if self._entry_patched is None:
            self._entry_patched = self.entry.__class__(self.entry)
        return self._entry_patched

    @property
    def exit(self) -> Optional[_Frame]:
        """Exit frame.

        Returns:
            the frame of the exit of the element.
        """
        if self._exit is None:
            self._exit = self.entry_patched.__class__(self.entry_patched)
        return self._exit

    @property
    def exit_patched(self) -> Optional[_Frame]:
        """Exit patched frame.

        Returns:
            the frame of the exit of the element with the patch applied.
        """
        if self._exit_patched is None:
            self._exit_patched = self.exit.__class__(self.exit)
        return self._exit_patched

    @property
    def frenet_orientation(self) -> Optional[_Frame]:
        if self._frenet is None:
            self._frenet = self.entry_patched.__class__(self.entry_patched)
        return self._frenet

    @property
    def center(self) -> Optional[_Frame]:
        """Center frame.

        Returns:
            the frame of the center of the element.
        """
        if self._center is None:
            self._center = self.entry.__class__(self.entry)
        return self._center

    @property
    def reference_trajectory(self) -> _pd.DataFrame:
        """

        Returns:

        """
        return self._reference_trajectory

    @reference_trajectory.setter
    def reference_trajectory(self, ref: _pd.DataFrame):
        """

        Args:
            ref:

        Returns:

        """
        self._reference_trajectory = ref

    @property
    def entry_s(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return self.reference_trajectory['S'].min() * _ureg.m
        else:
            return 0.0 * _ureg.m

    @property
    def exit_s(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return self.reference_trajectory['S'].max() * _ureg.m
        else:
            return 0.0 * _ureg.m

    @property
    def optical_length(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return (self.reference_trajectory['S'].max() - self.reference_trajectory['S'].min()) * _ureg.m
        else:
            return 0.0 * _ureg.m
