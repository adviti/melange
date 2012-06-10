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

"""Views for creating/editing GCI Tasks.
"""


import datetime

from google.appengine.ext import db

from django import forms as django_forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.views import forms
from soc.views.helper import access_checker
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gci.logic import profile as profile_logic
from soc.modules.gci.models import task
from soc.modules.gci.models.task import DIFFICULTIES
from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.views import forms as gci_forms
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper.url_patterns import url


DEF_TASK_TYPE_HELP_MSG = ugettext(
    'The kind of work to be done. Can be of more than one type')


def mentorChoicesForOrg(task, org):
  """Builds the tuple of mentor choice 2-tuples for the Django choice field.

  Args:
    task: GCITask entity for which the create page is being created
    org: The organization entity for which the mentor choices should be
         constructed.
  """
  mentors = profile_logic.queryAllMentorsForOrg(org)
  return ((str(m.key()), m.name()) for m in mentors)


class TaskEditPostClaimForm(gci_forms.GCIModelForm):
  """Django form for the task editing after the task is published page.
  """

  tags = django_forms.CharField(
      required=False,
      label=ugettext('Tags'),
      help_text=ugettext('Describe this task with tags (comma separated). '
                         'Ex: Linux, Apache, C++, GUI'))

  def __init__(self, data, *args, **kwargs):
    super(TaskEditPostClaimForm, self).__init__(*args, **kwargs)

    self.request_data = data
    self.organization = self.request_data.organization if not self.instance \
        else self.instance.org

    self.POST = args[0] if len(args) > 0 and args[0] else None

    mentor_choices = list(mentorChoicesForOrg(self.instance, self.organization))

    self.fields['mentors'] = django_forms.MultipleChoiceField(
        label=ugettext('Mentors'), required=False,
        widget=gci_forms.MultipleSelectWidget(
        attrs={
            'select_id': 'assign-mentor',
            'wrapper_id': 'select-mentors-wrapper',
            'add_new_text': 'add another mentor',
            }, disabled_option=('', 'Select a mentor')),
        choices=mentor_choices)

    if self.instance:
      self.fields['tags'].initial = ', '.join(self.instance.tags)

    # Bind all the fields here to boundclass since we do not iterate
    # over the fields using iterator for this form.
    self.bound_fields = {}
    for name, field in self.fields.items():
      self.bound_fields[name] = gci_forms.GCIBoundField(self, field, name)

  def save(self, commit=True):
    self.cleaned_data['modified_by'] = self.request_data.profile

    entity = super(TaskEditPostClaimForm, self).save(commit=False)

    if commit:
      entity.put()

    return entity

  def clean_tags(self):
    tags = []
    for tag in self.data.get('tags').split(','):
      tags.append(tag.strip())
    return tags
    
  def clean_mentors(self):
    mentor_key_strs = self.data.getlist('mentors')

    if not mentor_key_strs:
      raise django_forms.ValidationError(
          ugettext("At least one mentor should be assigned to the task."))

    org_mentors_keys = profile_logic.queryAllMentorsForOrg(
        self.organization, keys_only=True)

    mentor_keys = []
    for m_str in mentor_key_strs:
      if not m_str:
        break

      mentor_key = db.Key(m_str)
      if mentor_key not in org_mentors_keys:
        raise django_forms.ValidationError(
            ugettext("One of the mentors doesn't belong to the organization "
                     "that this task belongs to."))

      mentor_keys.append(mentor_key)

    return mentor_keys

  class Meta:
    model = task.GCITask
    css_prefix = 'gci-task'
    fields = ['mentors']


class TaskCreateForm(TaskEditPostClaimForm):
  """Django form for the task creation page.
  """

  time_to_complete_days = django_forms.IntegerField(
      label=ugettext('Time to complete'), min_value=0,
      error_messages={'min_value': ugettext('Days cannot be negative.')})

  time_to_complete_hours = django_forms.IntegerField(
      label=ugettext('Time to complete'), min_value=0,
      error_messages={'min_value': ugettext('Hours cannot be negative.')})

  def __init__(self, data, *args, **kwargs):
    super(TaskCreateForm, self).__init__(data, *args, **kwargs)

    difficulties = [(d, d) for d in DIFFICULTIES[:-1]]
    self.fields['difficulty_level'] = django_forms.ChoiceField(
        label=ugettext('Difficulty'), choices=difficulties)

    types = []
    for t in data.program.task_types:
      types.append((t, t))

    self.fields['types'] = django_forms.MultipleChoiceField(
        label=ugettext('Type'), choices=types,
        widget=gci_forms.CheckboxSelectMultiple,
        help_text=DEF_TASK_TYPE_HELP_MSG)

    if self.instance:
      self.fields['types'].initial = [str(t) for t in self.instance.types]
      ttc = datetime.timedelta(hours=self.instance.time_to_complete)
      self.fields['time_to_complete_days'].initial = ttc.days
      self.fields['time_to_complete_hours'].initial = ttc.seconds / 3600

      self.fields['difficulty_level'].initial = self.instance.difficulty_level

    # Bind all the fields here to boundclass since we do not iterate
    # over the fields using iterator for this form.
    for name, field in self.fields.items():
      self.bound_fields[name] = gci_forms.GCIBoundField(self, field, name)

  def create(self, commit=True, key_name=None, parent=None):
    # organization and status are in this create method and not in cleaner
    # because we want to store it in the entity only when it is created an
    # not while editing.
    organization = self.organization
    self.cleaned_data['org'] = organization

    profile = self.request_data.profile
    self.cleaned_data['created_by'] = profile
    self.cleaned_data['modified_by'] = profile

    entity = super(TaskCreateForm, self).create(
        commit=False, key_name=key_name, parent=parent)

    if commit:
      entity.put()

    if organization.key() in self.request_data.org_admin_for:
      entity.status = 'Unpublished'
    elif organization.key() in self.request_data.mentor_for:
      entity.status = 'Unapproved'

    return entity

  clean_description = cleaning.clean_html_content('description')

  def clean(self):
    super(TaskCreateForm, self).clean()

    cleaned_data = self.cleaned_data
    ttc_days = cleaned_data.get("time_to_complete_days", 0)
    ttc_hours = cleaned_data.get("time_to_complete_hours", 0)

    if ttc_days or ttc_hours:
      ttc_total = ttc_days * 24 + ttc_hours
      # We check if the time to complete is under 30 days because Google
      # Appengine task queue API doesn't let us to add a Appengine task
      # the queue with an ETA longer than 30 days. We use this ETA feature
      # for GCI tasks to automatically trigger the reminders for the task
      # after the deadline.
      if ttc_total <= 720:
        cleaned_data['time_to_complete'] = ttc_days * 24 + ttc_hours
      else:
        errors = self._errors.setdefault('time_to_complete_days', ErrorList())
        errors.append(ugettext('Time to complete must be less than 30 days.'))
    else:
      errors = self._errors.setdefault('time_to_complete_days', ErrorList())
      errors.append(ugettext('Time to complete must be specified.'))

    # Disallow "Unknown" difficulty
    if 'difficulty' in cleaned_data and \
        cleaned_data['difficulty'] not in DIFFICULTIES[:-1]:
      raise django_forms.ValidationError('Unknown difficulty is not supported')

    return cleaned_data

  class Meta:
    model = task.GCITask
    css_prefix = 'gci-task'
    fields = ['title', 'description', 'difficulty_level', 'mentors']


class TaskFormErrorTemplate(Template):
  """Task forms error message template.
  """

  def __init__(self, data, error):
    self.data = data
    self.error = error

  def context(self):
    return {
      'error': self.error,
    }

  def templatePath(self):
    return "v2/modules/gci/task_create/_error_msg.html"


class TaskEditFormTemplate(Template):
  """Task edit form template to use.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    if self.data.task:
      if self.data.full_edit:
        form_class = TaskCreateForm
      else:
        form_class = TaskEditPostClaimForm

      form = form_class(self.data, self.data.POST or None,
                        instance=self.data.task)
      title = "Edit task - %s" % (self.data.task.title)
    else:
      form = TaskCreateForm(self.data, self.data.POST or None)
      title = "Create a new task"

    return {
      'title':  title,
      'form': form,
      'full_edit': self.data.full_edit,
      'error': TaskFormErrorTemplate(self.data, form.errors),
    }

  def templatePath(self):
    if self.data.task and not self.data.full_edit:
      return "v2/modules/gci/task_create/_post_claim_edit.html"
    else:
      return "v2/modules/gci/task_create/_full_edit.html"


class TaskCreatePage(RequestHandler):
  """View to create a new task.
  """

  def djangoURLPatterns(self):
    return [
        url(r'task/create/%s$' % url_patterns.ORG,
            self, name='gci_create_task'),
        url(r'task/edit/%s$' % url_patterns.ID,
            self, name='gci_edit_task'),
    ]

  def checkAccess(self):
    self.mutator.taskFromKwargsIfId()

    self.check.isLoggedIn()

    assert access_checker.isSet(self.data.task)

    if self.data.task:
      self.check.checkCanUserEditTask()
      self.check.checkTimelineAllowsTaskEditing()

      # Set full_edit status depending on the task status
      self.mutator.fullEdit(self.check.hasTaskEditableStatus())
    else:
      self.check.canCreateTask()

  def templatePath(self):
    return 'v2/modules/gci/task_create/base.html'

  def context(self):
    if self.data.task:
      page_name = "Edit task - %s" % (self.data.task.title)
    else:
      page_name = "Create a new task"

    return {
      'page_name':  page_name,
      'task_edit_form_template': TaskEditFormTemplate(self.data),
    }

  def createTaskFromForm(self):
    """Creates a new task based on the data inserted in the form.

    Returns:
      a newly created task entity or None.
    """
    if self.data.task:
      if self.data.full_edit:
        form_class = TaskCreateForm
      else:
        form_class = TaskEditPostClaimForm

      form = form_class(self.data, self.data.POST, instance=self.data.task)
    else:
      form = TaskCreateForm(self.data, self.data.POST)

    if not form.is_valid():
      return None

    form.cleaned_data['program'] = self.data.program

    # The creator of the task and all the mentors for the task who have
    # have enabled "Subscribe automatically for the tasks" should be
    # subscribed to this task.
    mentor_keys = form.cleaned_data.get('mentors', None)
    mentor_entities = db.get(mentor_keys)
    subscribers = mentor_entities + [self.data.profile]

    keys = [i.key() for i in subscribers if i.automatic_task_subscription]

    form.cleaned_data['subscribers'] = list(set(keys))

    if not self.data.task:
      entity = form.create(commit=True)
    else:
      entity = form.save(commit=True)

    return entity

  def post(self):
    task = self.createTaskFromForm()
    if task:
      r = self.redirect.id(id=task.key().id_or_name())
      r.to('gci_edit_task', validated=True)
    else:
      self.get()
