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
implementation of the API.

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

    def prepare(self):
        """Prepare the provider for deployment.

        """
        self.private.prepare()

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
