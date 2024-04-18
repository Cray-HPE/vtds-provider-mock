#
# MIT License
#
# (C) Copyright [2024] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Public API module for the mock provider layer, this gives callers
access to the Provider API and prevents them from seeing the private
specific implementation of the API.

"""

from vtds_base import ContextualError
from .private.private_provider import PrivateProvider


class LayerAPI:
    """ Provider class presents the Provider API to callers.

    """
    def __init__(self, stack, config, build_dir):
        """Constructor. Constructs the public API to be used for
        building and interacting with a provider layer based on the
        full stack of vTDS layers loaded, the 'config' data structure
        provided and an absolute path to the 'build_dir' which is a
        scratch area provided by the caller for any provider layer
        build activities to take place.

        """
        self.stack = stack
        provider_config = config.get('provider', None)
        if provider_config is None:
            raise ContextualError(
                "no provider configuration found in top level configuration"
            )
        self.private = PrivateProvider(stack, provider_config, build_dir)
        self.prepared = False
        self.deployed = False

    def prepare(self):
        """Prepare the provider for deployment.

        """
        self.private.prepare()
        self.prepared = True

    def validate(self):
        """Run any configuration validation that may be appropriate
        for the provider layer.

        """
        self.private.validate()

    def deploy(self):
        """Deploy the provider (must call prepare() prior to this
        call.

        """
        self.private.deploy()

    def shutdown(self, virtual_blade_names=None):
        """Shutdown operation. This will shut down (power off) the
        specified virtual blades, or, if none are specified, all
        virtual blades, in the provider, leaving them provisioned.

        """
        self.private.shutdown(virtual_blade_names)

    def startup(self, virtual_blade_names=None):
        """Startup operation. This will start up (power on) the
        specified virtual blades, or, if none are specified, all
        virtual blades, in the provider as long as they are
        provisioned.

        """
        self.private.startup(virtual_blade_names)

    def dismantle(self):
        """Dismantle operation. This will de-provision all virtual
        blades in the provider.

        """
        self.private.dismantle()

    def restore(self):
        """Restore operation. This will re-provision deprovisioned
        virtual blades in the provider.

        """
        self.private.restore()

    def remove(self):
        """Remove operation. This will remove all resources
        provisioned for the provider layer.

        """
        self.private.remove()

    def get_virtual_blades(self):
        """Return a the VirtualBlades object containing all of the
        available non-pure-base-class Virtual Blades.

        """
        return self.private.get_virtual_blades()

    def get_blade_interconnects(self):
        """Return a BladeInterconnects object containing all the
        available non-pure-base-class Blade Interconnects.

        """
        return self.private.get_blade_interconnects()
