# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing the GCI Callback.
"""


from soc.modules.gci.tasks.updates import role_conversion


class Callback(object):
  """Callback object that handles interaction between the core.
  """

  API_VERSION = 1

  def __init__(self, core):
    """Initializes a new Callback object for the specified core.
    """

    self.core = core
    self.views = []

  def registerViews(self):
    """Instantiates all view objects.
    """
    from soc.modules.gci.views import accepted_orgs
    from soc.modules.gci.views import admin
    from soc.modules.gci.views import age_check
    from soc.modules.gci.views import all_tasks
    from soc.modules.gci.views import bulk_create
    from soc.modules.gci.views import dashboard
    from soc.modules.gci.views import delete_account
    from soc.modules.gci.views import document
    from soc.modules.gci.views import homepage
    from soc.modules.gci.views import invite
    from soc.modules.gci.views import leaderboard
    from soc.modules.gci.views import org_app
    from soc.modules.gci.views import org_home
    from soc.modules.gci.views import org_profile
    from soc.modules.gci.views import participants
    from soc.modules.gci.views import profile
    from soc.modules.gci.views import profile_show
    from soc.modules.gci.views import program
    from soc.modules.gci.views import request
    from soc.modules.gci.views import student_forms
    from soc.modules.gci.views import students_info
    from soc.modules.gci.views import task
    from soc.modules.gci.views import task_list
    from soc.modules.gci.views import task_create

    self.views.append(accepted_orgs.AcceptedOrgsPage())
    self.views.append(accepted_orgs.AcceptedOrgsAdminPage())
    self.views.append(admin.DashboardPage())
    self.views.append(admin.LookupLinkIdPage())
    self.views.append(all_tasks.TaskListPage())
    self.views.append(age_check.AgeCheck())
    self.views.append(bulk_create.BulkCreate())
    self.views.append(dashboard.DashboardPage())
    self.views.append(delete_account.DeleteAccountPage())
    self.views.append(document.DocumentPage())
    self.views.append(document.EditDocumentPage())
    self.views.append(document.EventsPage())
    self.views.append(document.DocumentListPage())
    self.views.append(homepage.Homepage())
    self.views.append(invite.InvitePage())
    self.views.append(invite.ManageInvite())
    self.views.append(invite.RespondInvite())
    self.views.append(invite.ListUserInvitesPage())
    self.views.append(leaderboard.LeaderboardPage())
    self.views.append(leaderboard.StudentTasksPage())
    self.views.append(org_app.GCIOrgAppEditPage())
    self.views.append(org_profile.OrgProfilePage())
    self.views.append(org_app.GCIOrgAppPreviewPage())
    self.views.append(org_app.GCIOrgAppRecordsList())
    self.views.append(org_app.GCIOrgAppShowPage())
    self.views.append(org_app.GCIOrgAppTakePage())
    self.views.append(org_home.OrgHomepage())
    self.views.append(participants.MentorsListAdminPage())
    self.views.append(profile.GCIProfilePage())
    self.views.append(profile_show.GCIProfileShowPage())
    self.views.append(program.ProgramPage())
    self.views.append(program.TimelinePage())
    self.views.append(request.SendRequestPage())
    self.views.append(request.ManageRequestPage())
    self.views.append(request.RespondRequestPage())
    self.views.append(student_forms.StudentFormUpload())
    self.views.append(student_forms.StudentFormDownload())
    self.views.append(students_info.StudentsInfoPage())
    self.views.append(task.TaskViewPage())
    self.views.append(task.WorkSubmissionDownload())
    self.views.append(task_list.TaskListPage())
    self.views.append(task_create.TaskCreatePage())

    # Google Appengine Tasks
    from soc.modules.gci.tasks.bulk_create import BulkCreateTask
    from soc.modules.gci.tasks.ranking_update import RankingUpdater
    from soc.modules.gci.tasks.task_update import TaskUpdate

    self.views.append(BulkCreateTask())
    self.views.append(RankingUpdater())
    self.views.append(TaskUpdate())

  def registerWithSitemap(self):
    """Called by the server when sitemap entries should be registered.
    """

    self.core.requireUniqueService('registerWithSitemap')

    # Redesigned view registration
    for view in self.views:
      self.core.registerSitemapEntry(view.djangoURLPatterns())

    self.core.registerSitemapEntry(role_conversion.getDjangoURLPatterns())

  def registerWithProgramMap(self):
    """Called by the server when program_map entries should be registered.
    """

    self.core.requireUniqueService('registerWithProgramMap')

    from soc.modules.gci.models.program import GCIProgram
    program_entities = GCIProgram.all().fetch(1000)
    map = ('GCI Programs', [
        (str(e.key()), e.name) for e in program_entities])

    self.core.registerProgramEntry(map)
