#!/usr/bin/env python
#
# Copyright 2016 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Create configuration for model openconfig-mpls.

usage: gn-create-oc-mpls-40-ydk.py [-h] [-v] device

positional arguments:
  device         gNMI device (http://user:password@host:port)

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  print debugging messages
"""

from argparse import ArgumentParser
from urlparse import urlparse

from ydk.path import Repository
from ydk.services import CRUDService
from ydk.gnmi.providers import gNMIServiceProvider
from ydk.models.openconfig import openconfig_network_instance \
    as oc_network_instance
from ydk.models.openconfig import openconfig_mpls \
    as oc_mpls
import os
import logging


YDK_REPO_DIR = os.path.expanduser("~/.ydk/")


def config_mpls(network_instances):
    """Add config data to mpls object."""
    # configure default network instance
    network_instance = network_instances.NetworkInstance()
    network_instance.name = "default"
    network_instance.config.name = "default"

    # constrained path
    named_explicit_path = network_instance.mpls.lsps.constrained_path.named_explicit_paths.NamedExplicitPath()
    named_explicit_path.name = "LER1-LSR1-LER2"
    named_explicit_path.config.name = "LER1-LSR1-LER2"

    # strict hop
    explicit_route_object = named_explicit_path.explicit_route_objects.ExplicitRouteObject()
    explicit_route_object.index = 10
    explicit_route_object.config.index = 10
    explicit_route_object.config.address = "172.16.1.1"
    explicit_route_object.config.hop_type = oc_mpls.MplsHopType.STRICT
    named_explicit_path.explicit_route_objects.explicit_route_object.append(explicit_route_object)

    # strict hop
    explicit_route_object = named_explicit_path.explicit_route_objects.ExplicitRouteObject()
    explicit_route_object.index = 20
    explicit_route_object.config.index = 20
    explicit_route_object.config.address = "172.16.1.5"
    explicit_route_object.config.hop_type = oc_mpls.MplsHopType.STRICT
    named_explicit_path.explicit_route_objects.explicit_route_object.append(explicit_route_object)
    network_instance.mpls.lsps.constrained_path.named_explicit_paths.named_explicit_path.append(named_explicit_path)
    network_instances.network_instance.append(network_instance)


if __name__ == "__main__":
    """Execute main program."""
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", help="print debugging messages",
                        action="store_true")
    parser.add_argument("device",
                        help="gNMI device (http://user:password@host:port)")
    args = parser.parse_args()
    device = urlparse(args.device)

    # log debug messages if verbose argument specified
    if args.verbose:
        logger = logging.getLogger("ydk")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(("%(asctime)s - %(name)s - "
                                      "%(levelname)s - %(message)s"))
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # create gNMI provider
    repository = Repository(YDK_REPO_DIR+device.hostname)
    provider = gNMIServiceProvider(repo=repository,
                                   address=device.hostname,
                                   port=device.port,
                                   username=device.username,
                                   password=device.password)
    # create CRUD service
    crud = CRUDService()

    network_instances = oc_network_instance.NetworkInstances()
    config_mpls(network_instances)  # add object configuration

    # create configuration on gNMI device
    crud.create(provider, network_instances)

    exit()
# End of script

