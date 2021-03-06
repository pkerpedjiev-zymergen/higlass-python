from ._version import version_info, __version__, EXTENSION_VERSION
import ipywidgets as widgets
from traitlets import Unicode
from traitlets import default
from traitlets import List
from traitlets import Dict
from traitlets import Int


class HiGlassDisplay(widgets.DOMWidget):
    _view_name = Unicode('HiGlassDisplayView').tag(sync=True)
    _model_name = Unicode('HiGlassDisplayModel').tag(sync=True)
    _view_module = Unicode('jupyter-higlass').tag(sync=True)
    _model_module = Unicode('jupyter-higlass').tag(sync=True)
    _view_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)

    _model_data = List([]).tag(sync=True)
    viewconf = Dict({}).tag(sync=True)
    hg_options = Dict({}).tag(sync=True)
    height = Int().tag(sync=True)

    def __init__(self, **kwargs):
        # self.viewconf = viewconf
        super(HiGlassDisplay, self).__init__(**kwargs)

    # @default('layout')
    # def _default_layout(self):
    #     return widgets.Layout(height='600px', align_self='stretch')

    # def set_data(self, js_data):
    #     self._model_data = js_data
