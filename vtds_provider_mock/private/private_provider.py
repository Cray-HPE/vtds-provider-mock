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
"""Private layer implementation module for the mock provider.

"""

from vtds_base import (
    ContextualError,
)
from .api_objects import (
    PrivateVirtualBlades,
    PrivateBladeInterconnects
)


class PrivateProvider:
    """PrivateProvider class, implements the mock provider layer
    accessed through the python Provider API.

    """
    def __init__(self, stack, config, build_dir):
        """Constructor, stash the root of the platfform tree and the
        digested and finalized provider configuration provided by the
        caller that will drive all activities at all layers.

        """
        self.config = config
        self.stack = stack
        self.build_dir = build_dir
        self.prepared = False

    def prepare(self):
        """Prepare operation. This drives creation of the provider
        layer definition and any configuration that need to be driven
        down into the provider layer to be ready for deployment.

        """
        self.prepared = True
        print("Preparing vtds-provider-mock")

    def validate(self):
        """Run the terragrunt plan operation on a prepared mock
        provider layer to make sure that the configuration produces a
        useful result.

        """
        if not self.prepared:
            raise ContextualError(
                "cannot validate an unprepared provider, "
                "call prepare() first"
            )
        print("Validating vtds-provider-mock")

    def deploy(self):
        """Deploy operation. This drives the deployment of provider
        layer resources based on the layer definition. It can only be
        called after the prepare operation (prepare()) completes.

        """
        if not self.prepared:
            raise ContextualError(
                "cannot deploy an unprepared provider, call prepare() first"
            )
        print("Deploying vtds-provider-mock")

    def shutdown(self, virtual_blade_names):
        """Shutdown operation. This will shut down (power off) the
        specified virtual blades, or, if none are specified, all
        virtual blades, in the provider, leaving them provisioned.

        """
        print(
            "Shutting down nodes in vtds-provider-mock: %s" % (
                str(virtual_blade_names)
            )
        )

    def startup(self, virtual_blade_names):
        """Startup operation. This will start up (power on) the
        specified virtual blades, or, if none are specified, all
        virtual blades, in the provider as long as they are
        provisioned.

        """
        print(
            "Starting up nodes in vtds-provider-mock: %s" % (
                str(virtual_blade_names)
            )
        )

    def dismantle(self):
        """Dismantle operation. This will de-provision all virtual
        blades in the provider.

        """
        if not self.prepared:
            raise ContextualError(
                "cannot dismantle an unprepared provider, call prepare() first"
            )
        print("Dismantling vtds-provider-mock")

    def restore(self):
        """Restore operation. This will re-provision deprovisioned
        virtual blades in the provider.

        """
        if not self.prepared:
            raise ContextualError(
                "cannot restore an unprepared provider, call prepare() first"
            )
        print("Restoring vtds-provider-mock")

    def remove(self):
        """Remove operation. This will remove all resources
        provisioned for the provider layer.

        """
        if not self.prepared:
            raise ContextualError(
                "cannot deploy an unprepared provider, call prepare() first"
            )
        print("Removing vtds-provider-mock")

    def get_virtual_blades(self):
        """Return a the VirtualBlades object containing all of the
        available non-pure-base-class Virtual Blades.

        """
        return PrivateVirtualBlades(self.config)

    def get_blade_interconnects(self):
        """Return a BladeInterconnects object containing all the
        available non-pure-base-class Blade Interconnects.

        """
        return PrivateBladeInterconnects(self.config)
