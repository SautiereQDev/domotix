from domotix.models import Light

from . import DeviceRepository


class LightRepository(DeviceRepository):

    def __init__(self, light: Light, is_on: bool = False):
        # super.__init__()
        pass
