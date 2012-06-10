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

"""Module for storing GCI related URL names.
"""


GCI_LIST_ORG_INVITES = 'gci_list_org_invites'
GCI_LIST_INVITES = 'gci_list_invites'
GCI_MANAGE_INVITE = 'gci_manage_invite'
GCI_RESPOND_INVITE = 'gci_respond_invite'
GCI_SEND_INVITE = 'gci_send_invite'

GCI_MANAGE_REQUEST = 'gci_manage_request'
GCI_RESPOND_REQUEST = 'gci_respond_request'
GCI_SEND_REQUEST = 'gci_send_request'

GCI_LEADERBOARD = 'gci_leaderboard'
GCI_STUDENT_TASKS = 'gci_student_tasks'
GCI_STUDENT_FORM_DOWNLOAD = 'gci_student_form_download'

CREATE_GCI_ORG_PROFILE = 'create_gci_org_profile'
EDIT_GCI_ORG_PROFILE = 'edit_gci_org_profile'
GCI_ORG_HOME = 'gci_org_home'

GCI_VIEW_TASK = 'gci_view_task'


# GET PARAMETERS WHICH ARE USED THROUGHOUT THE MODULE
#TODO(dhans): consider creation of a separate module for that
"""GET parameter which should be set in order to download Consent Form.
"""
CONSENT_FORM_GET_PARAM = 'consent_form'

"""GET parameter which should be set in order to download Student ID Form.
"""
STUDENT_ID_FORM_GET_PARAM = 'student_id_form'

GCI_STUDENTS_INFO = 'gci_students_info'