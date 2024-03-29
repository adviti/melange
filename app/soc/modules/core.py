# Copyright 2009 the Melange authors.
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

"""The Melange Core module.
"""


import logging

from django.conf.urls import defaults

import soc.cache.sidebar


class Error(Exception):
  """Error class for the callback module.
  """

  pass


class APIVersionMismatch(Error):
  """Error raised when API version mismatches.
  """

  MISMATCH_MSG_FMT = "API mismatch, expected '%d', got '%d'."

  def __init__(self, expected, actual):
    """Instantiates a new exception with a customized message.
    """

    msg = self.MISMATCH_MSG_FMT % (expected, actual)
    super(APIVersionMismatch, self).__init__(msg)


class MissingService(Error):
  """Error raised when a required service is missing.
  """

  MISSING_SERVICE_FMT = "Required service '%s' is not registered, known: %s"

  def __init__(self, service, services):
    """Instantiates a new exception with a customized message.
    """

    msg = self.MISSING_SERVICE_FMT % (service, services)
    super(MissingService, self).__init__(msg)


class MissingCapability(Error):
  """Error raised when a required capability is missing.
  """

  MISSING_CAPABILITY_FMT = "Required capability '%s' " + \
      "is not registered, known: %s"

  def __init__(self, capability, capabilities):
    """Instantiates a new exception with a customized message.
    """

    msg = self.MISSING_CAPABILITY_FMT % (capability, capabilities)
    super(MissingCapability, self).__init__(msg)


class NonUniqueService(Error):
  """Error raised when a required service is missing.
  """

  NON_UNIQUE_SERVICE_FMT = "Unique service '%s' called a 2nd time, known: %s."

  def __init__(self, service, services):
    """Instantiates a new exception with a customized message.
    """

    msg = self.NON_UNIQUE_SERVICE_FMT % (service, services)
    super(NonUniqueService, self).__init__(msg)


class AlreadyRegisteredRight(Error):
  """Error raised when a right is registrated a second time
  """

  ALREADY_REGISTERED_RIGHT_FMT = "Tried to register right '%s' a second time."

  def __init__(self, right):
    """Instantiates a new exception with a customized message.
    """

    msg = self.ALREADY_REGISTERED_RIGHT_FMT % right
    super(AlreadyRegisteredRight, self).__init__(msg)


class Core(object):
  """The core handler that controls the Melange API.
  """

  def __init__(self):
    """Creates a new instance of the Core.
    """
    
    # pylint: disable=C0103
    self.API_VERSION = 1

    self.registered_callbacks = []
    self.capabilities = []
    self.services = []

    self.sitemap = []
    self.program_map = []

  ##
  ## internal
  ##

  def getService(self, callback, service):
    """Retrieves the specified service from the callback if supported.

    Args:
     callback: the callback to retrieve the capability from
     service: the service to retrieve
    """

    if not hasattr(callback, service):
      return False

    func = getattr(callback, service)

    if not callable(func):
      return False

    return func

  def callService(self, service, unique, *args, **kwargs):
    """Calls the specified service on all callbacks.
    """

    if unique and (service in self.services):
      return

    results = []

    for callback in self.registered_callbacks:
      func = self.getService(callback, service)
      if not func:
        continue

      result = func(*args, **kwargs)
      results.append(result)

    self.services.append(service)
    return results

  ##
  ## Core code
  ##

  def initialize(self):
    """Performs the required initialization for all modules.
    """

    self.callService('registerViews', True)

  def getPatterns(self):
    """Returns the Django patterns for this site.
    """

    self.callService('registerWithSitemap', True)
    return defaults.patterns(None, *self.sitemap)

  ###
  ### Core control code
  ###
  ### Called by other setup code to get the Core in a desired state.
  ###

  def registerModuleCallbacks(self, modules, fmt):
    """Retrieves all callbacks for the modules of this site.

    Callbacks for modules without a version number or the wrong API_VERSION
    number are dropped.  They won't be called.
    """

    modules = ['soc_core'] + modules
    modules = [__import__(fmt % i, fromlist=['']) for i in modules]

    for callback_class in [i.Callback for i in modules]:
      if callback_class.API_VERSION != self.API_VERSION:
        raise APIVersionMismatch(self.API_VERSION,
                                 callback_class.API_VERSION)


      callback = callback_class(self)
      self.registered_callbacks.append(callback)

    return True

  ##
  ## Module code
  ##

  def registerCapability(self, capability):
    """Registers the specified capability.
    """

    self.capabilities.append(capability)

  def requireCapability(self, capability):
    """Requires that the specified capability is present.
    """

    if capability in self.capabilities:
      return True

    raise MissingCapability(capability, self.capabilities)

  def requireService(self, service):
    """Requires that the specified service has been called.
    """

    if service in self.services:
      return True

    raise MissingService(service, self.services)

  def requireUniqueService(self, service):
    """Requires that the specified service is called exactly once.
    """

    if service not in self.services:
      return True

    raise NonUniqueService(service, self.services)

  def registerSitemapEntry(self, entries):
    """Registers the specified entries with the sitemap.
    """

    self.sitemap.extend(entries)

  def registerProgramEntry(self, entry):
    """Registers the specified module's programs with the core.
    """

    self.program_map.append(entry)

  def getProgramMap(self):
    """Returns a tuple containing all the programs for all the modules.

    It returns tuple for all the modules which have registered their
    Programs in the format required to field Django's choices parameter
    in the form fields.
    """

    self.callService('registerWithProgramMap', True)
    return self.program_map
