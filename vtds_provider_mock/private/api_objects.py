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
"""Private implementations of API objects.

"""
from contextlib import contextmanager

from vtds_base import (
    ContextualError
)
from ..api_objects import (
    VirtualBlades,
    BladeInterconnects,
    BladeConnection
)


# pylint: disable=invalid-name
class PrivateVirtualBlades(VirtualBlades):
    """The external representation of a class of Virtual Blades and
    the public operations that can be performed on blades in that
    class. Virtual Blade operations refer to individual blades by
    their instance number which is an integer greater than or equal to
    0 and less that the number of blade instances in the class.

    """
    def __init__(self, config):
        """Constructor

        """
        self.config = config

    def __get_blade(self, blade_type):
        """Class private: get the blade configuration for the named
        blade type and return it.

        """
        blade = (
            self.config.get('provider', {})
            .get('virtual_blades', {})
            .get(blade_type, None)
        )
        if blade is None:
            raise ContextualError(
                "unknown blade type '%s' specified"
            )
        return blade

    def __check_instance(self, blade_type, instance):
        """class private: Ensure that the specified instance number
        for a given blade type (blades) is legal.

        """
        if not isinstance(instance, int):
            raise ContextualError(
                "Virtual Blade instance number must be integer not '%s'" %
                type(instance)
            )
        blade = self.__get_blade(blade_type)
        count = int(blade.get('count'), 0)
        if instance < 0 or instance >= count:
            raise ContextualError(
                "instance number %d out of range for Virtual Blade "
                "type '%s' which has a count of %d" %
                (instance, blade_type, count)
            )

    def blade_types(self):
        """Get a list of virtual blade types that are not pure base
        classes by name.

        """
        virtual_blades = self.config.get('virtual_blades', {})
        return [
            name for name in virtual_blades
            if not virtual_blades[name].get('pure_base_class', False)
        ]

    def blade_count(self, blade_type):
        """Get the number of Virtual Blade instances of the specified
        type.

        """
        blade = self.__get_blade(blade_type)
        return int(blade.get('count', 0))

    def blade_interconnects(self, blade_type):
        """Return the list of Blade Interconnects by name connected to
        the specified type of Virtual Blade.

        """
        blade = self.__get_blade(blade_type)
        return [
            interconnect['name']
            for _, interconnect in blade.get('interconnects', {}).items()
        ]

    def blade_hostname(self, blade_type, instance):
        """Get the hostname of a given instance of the specified type
        of Virtual Blade.

        """
        self.__check_instance(blade_type, instance)
        blade = self.__get_blade(blade_type)
        return blade.get('hostnames', [])[instance]

    def blade_ip(self, blade_type, instance, interconnect):
        """Return the IP address (string) on the named Blade
        Interconnect of a specified instance of the named Virtual
        Blade type.

        """
        self.__check_instance(blade_type, instance)
        blade = self.__get_blade(blade_type)
        return blade.get('ips', [])[instance]

    @contextmanager
    def connect_blade(self, remote_port, blade_type, instance):
        """Establish an external connection to the specified remote
        port on the specified instance of the named Virtual Blade
        type. Return a context manager (suitable for use in a 'with'
        clause) yielding a BladeConnection object for the
        connection. Upon leaving the 'with' context, the connection in
        the BladeConnection is closed.

        """
        hostname = self.blade_hostname(blade_type, instance)
        connection = PrivateBladeConnection(
            hostname, remote_port, blade_type
        )
        try:
            yield connection
        finally:
            # This is a layer private operation not really class
            # private. Treat this reference as friendly.
            connection._disconnect()  # pylint: disable=protected-access

    @contextmanager
    def connect_blades(self, remote_port, blade_types=None):
        """Establish external connections to the specified remote port
        on all the Virtual Blade instances on all the Virtual Blade
        types listed by name in 'blade_types'. If 'blade_types' is not
        provided or None, all available blade types are used. Return a
        context manager (suitable for use in a 'with' clause) yielding
        the list of APIBladeConnection objects representing the
        connections. Upon leaving the 'with' context, all the
        connections in the resulting list are closed.

        """
        virtual_blades = (
            self.config.get('provider', {}).get('virtual_blades', {})
        )
        blade_types = (
            blade_types if blade_types is not None else
            [
                name for name in virtual_blades
                if not virtual_blades[name].get('pure_base_class', False)
            ]
        )
        connections = [
            PrivateBladeConnection(
                self.blade_hostname(blade_type, instance), remote_port,
                blade_type
            )
            for blade_type in blade_types
            for instance in range(0, self.blade_count(blade_type))
        ]
        try:
            yield connections
        finally:
            for connection in connections:
                # This is a layer private operation not really class
                # private. Treat this reference as friendly.
                connection._disconnect()  # pylint: disable=protected-access


# pylint: disable=invalid-name
class PrivateBladeInterconnects(BladeInterconnects):
    """The external representation of the set of Blade Interconnects
    and public operations that can be performed on the interconnects.

    """
    def __init__(self, config):
        """Constructor

        """
        self.config = config

    def __interconnects_by_name(self):
        """Return a dictionary of non-pure-base-class interconnects
        indexed by 'network_name'

        """
        blade_interconnects = self.config.get("blade_interconnects", {})
        try:
            return {
                interconnect['network_name']: interconnect
                for _, interconnect in blade_interconnects.items()
                if not interconnect.get('pure_base_class', False)
            }
        except KeyError as err:
            # Unfortunately, because of the comprehension above, I don't
            # know which network had the problem, but I can at least report
            # which key was bad...
            raise ContextualError(
                "provider config error: 'network_name' not specified in "
                "one of the interconnects configured under "
                "'provider.blade_interconnects'"
            ) from err

    def interconnect_names(self):
        """Get a list of blade interconnects by name

        """
        return self.__interconnects_by_name().keys()

    def ipv4_cidr(self, interconnect_name):
        """Return the (string) IPv4 CIDR (<IP>/<length>) for the
        network on the named interconnect.

        """
        blade_interconnects = (
            self.config.get("provider", {}).get("blade_interconnects", {})
        )
        if interconnect_name not in blade_interconnects:
            raise ContextualError(
                "requestiong ipv4_cidr of unknown blade interconnect '%s'" %
                interconnect_name
            )
        interconnect = blade_interconnects.get(interconnect_name, {})
        if 'ipv4_cidr' not in interconnect:
            raise ContextualError(
                "provider layer configuration error: no 'ipv4_cidr' found in "
                "blade interconnect named '%s'" % interconnect_name
            )
        return interconnect['ipv4_cidr']


# pylint: disable=invalid-name
class PrivateBladeConnection(BladeConnection):
    """A class containing the relevant information needed to use
    external connections to ports on a specific Virtual Blade.

    """
    def __init__(self, hostname, remote_port, blade_type):
        """Constructor

        """
        self.hostname = hostname
        self.blade_type = blade_type
        self.remote_port = remote_port
        self.local_ip = "127.0.0.1"
        self.loc_port = None
        self._connect()

    def _connect(self):
        """Layer private operation: establish the connection and learn
        the local IP and port of the connection. This is really not done
        in the mock layer, there is no actual connection set up at all.

        """
        print(
            "Connecting to blade '%s'[%s] port %d" % (
                self.hostname, self.blade_type, self.remote_port
            )
        )
        self.loc_port = 12345

    def _disconnect(self):
        """Layer private operation: drop the connection.
        """
        self.loc_port = None

    def blade_type(self):
        """Return the name of the Virtual Blade type of the connected
        Virtual Blade.

        """
        return self.blade_type

    def blade_hostname(self):
        """Return the hostname of the connected Virtual Blade.

        """
        return self.hostname

    def local_ip(self):
        """Return the locally reachable IP address of the connection
        to the Virtual Blade.

        """
        return self.local_ip

    def local_port(self):
        """Return the TCP port number on the locally reachable IP
        address of the connection to the Virtual Blade.

        """
        return self.loc_port
