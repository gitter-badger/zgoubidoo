
PALETTE = {
    'solarized':  {'base03':  '#002b36',
                   'base02':  '#073642',
                   'base01':  '#586e75',
                   'base00':  '#657b83',
                   'base0':   '#839496',
                   'base1':   '#93a1a1',
                   'base2':   '#eee8d5',
                   'base3':   '#fdf6e3',
                   'yellow':  '#b58900',
                   'orange':  '#cb4b16',
                   'red':     '#dc322f',
                   'magenta': '#d33682',
                   'violet':  '#6c71c4',
                   'blue':    '#268bd2',
                   'cyan':    '#2aa198',
                   'green':   '#859900'
                   }
}
PALETTE['solarized']['gray'] = PALETTE['solarized']['base03']


class ZgoubiPlot:
    def __init__(self, with_boxes=True, with_frames=True):
        self._with_boxes = with_boxes
        self._with_frames = with_frames
        self._palette = PALETTE['solarized']

    def cartesian_bend(self, **kwargs):
        pass

    def polar_bend(self, **kwargs):
        pass