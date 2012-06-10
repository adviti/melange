#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Set of available avatars to choose.
"""


# mapping of avatar colors to their relative path
AVATAR_COLORS = {
    'blue': '%d-blue.jpg',
    'brown': '%d-brown.jpg',
    'green': '%d-green.jpg',
    'orange': '%d-orange.jpg',
    'pink': '%d-pink.jpg',
    'purple': '%d-purple.jpg',
    'red': '%d-red.jpg',
    }

# List of avatars
AVATARS = [c % i for i in range(1, 27) for _, c in AVATAR_COLORS.items()]

# List of avatars grouped by color
AVATARS_BY_COLOR = dict((k, [c % i for i in range(1, 27)]) for k, c in AVATAR_COLORS.items())

# List of available colors
COLORS = sorted(AVATAR_COLORS.keys())
