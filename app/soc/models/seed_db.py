#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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

"""Seeds or clears the datastore.
"""


import itertools
import logging
import random
import datetime

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from django import http

from soc.logic import accounts
from soc.logic import dicts
from soc.logic import user
from soc.models.document import Document
from soc.models.host import Host
from soc.models.notification import Notification

from soc.models.site import Site
from soc.models.sponsor import Sponsor

from soc.models.survey import Survey
from soc.models.survey_record import SurveyRecord

from soc.models.user import User

from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.program import GCIProgram
from soc.modules.gci.models.score import GCIScore
from soc.modules.gci.models.student import GCIStudent
from soc.modules.gci.models.timeline import GCITimeline
from soc.modules.gci.models.profile import GCIStudentInfo
from soc.modules.gci.models.task import DifficultyLevel
from soc.modules.gci.models.task import GCITask

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.profile import GSoCStudentInfo
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.student_project import StudentProject
from soc.modules.gsoc.models.student_proposal import StudentProposal
from soc.modules.gsoc.models.timeline import GSoCTimeline


def seed(request, *args, **kwargs):
  """Seeds the datastore with some default values.
  """

  site_properties = {
      'key_name': 'site',
      'link_id': 'site',
      }

  site = Site(**site_properties)
  site.put()

  account = accounts.getCurrentAccount()

  if not account:
    account = users.User(email='test@example.com')

  user_properties = {
      'key_name': 'test',
      'link_id': 'test',
      'account': account,
      'name': 'Test',
      }

  current_user = User(**user_properties)
  current_user.put()

  group_properties = {
       'key_name': 'google',
       'link_id': 'google',
       'name': 'Google Inc.',
       'short_name': 'Google',
       'founder': current_user,
       'home_page': 'http://www.google.com',
       'email': 'ospo@google.com',
       'description': 'This is the profile for Google.',
       'contact_street': 'Some Street',
       'contact_city': 'Some City',
       'contact_country': 'United States',
       'contact_postalcode': '12345',
       'phone': '1-555-BANANA',
       'status': 'active',
       }

  google = Sponsor(**group_properties)
  google.put()


  role_properties = {
      'key_name': 'google/test',
      'link_id': 'test',
      'public_name': 'test',
      'scope': google,
      'scope_path': 'google',
      'user': current_user,
      'given_name': 'Test',
      'surname': 'Example',
      'name_on_documents': 'Test Example',
      'email': 'test@example.com',
      'res_street': 'Some Street',
      'res_city': 'Some City',
      'res_state': 'Some State',
      'res_country': 'United States',
      'res_postalcode': '12345',
      'phone': '1-555-BANANA',
      'birth_date': db.DateProperty.now(),
      'agreed_to_tos': True,
      'is_org_admin': True,
      'is_mentor': True,
      }


  current_user.host_for = [google.key()]
  current_user.put()

  google_host = Host(**role_properties)
  google_host.put()

  from datetime import datetime
  from datetime import timedelta

  now = datetime.now()
  before = now - timedelta(365)
  after = now + timedelta(365)

  timeline_properties = {
      'key_name': 'google/gsoc2009',
      'link_id': 'gsoc2009',
      'scope_path': 'google',
      'scope': google,
      'program_start': before,
      'program_end': after,
      'accepted_organization_announced_deadline': before,
      'student_signup_start': before,
      'student_signup_end': after,
  }

  gsoc2009_timeline = GSoCTimeline(**timeline_properties)
  gsoc2009_timeline.put()


  program_properties = {
      'key_name': 'google/gsoc2009',
      'link_id': 'gsoc2009',
      'scope_path': 'google',
      'scope': google,
      'name': 'Google Summer of Code 2009',
      'short_name': 'GSoC 2009',
      'group_label': 'GSOC',
      'description': 'This is the program for GSoC 2009.',
      'apps_tasks_limit': 42,
      'slots': 42,
      'timeline': gsoc2009_timeline,
      'status': 'visible',
      }

  gsoc2009 = GSoCProgram(**program_properties)
  gsoc2009.put()


  timeline_properties.update({
      'key_name': 'google/gsoc2010',
      'link_id': 'gsoc2010',
  })

  gsoc2010_timeline = GSoCTimeline(**timeline_properties)
  gsoc2010_timeline.put()

  program_properties.update({
      'key_name': 'google/gsoc2010',
      'link_id': 'gsoc2010',
      'name': 'Google Summer of Code 2010',
      'description': 'This is the program for GSoC 2010.',
      'short_name': 'GSoC 2010',
      'timeline': gsoc2010_timeline,
  })

  gsoc2010 = GSoCProgram(**program_properties)
  gsoc2010.put()

  timeline_properties = {
        'key_name': 'google/gci2009',
        'link_id': 'gci2009',
        'scope_path': 'google',
        'scope': google,
        'program_start': before,
        'program_end': after,
        'accepted_organization_announced_deadline': before,
        'student_signup_start': before,
        'student_signup_end': after,
        'tasks_publicly_visible': before,
        'task_claim_deadline': after,
        'stop_all_work_deadline': after,
  }

  gci2009_timeline = GCITimeline(**timeline_properties)
  gci2009_timeline.put()


  program_properties.update({
      'key_name': 'google/gci2009',
      'link_id': 'gci2009',
      'name': 'Google Code In Contest 2009',
      'short_name': 'GCI 2009',
      'group_label': 'GCI',
      'description': 'This is the program for GCI 2009.',
      'timeline': gci2009_timeline,
      })

  gci2009 = GCIProgram(**program_properties)
  gci2009.put()

  site.active_program = gci2009
  site.put()


  group_properties.update({
    'key_name': 'google/gci2009/melange',
    'link_id': 'melange',
    'name': 'Melange Development Team',
    'short_name': 'Melange',
    'scope_path': 'google/gci2009',
    'scope': gci2009,
    'home_page': 'http://code.google.com/p/soc',
    'description': 'Melange, share the love!',
    'license_name': 'Apache License',
    'ideas': 'http://code.google.com/p/soc/issues',
    })

  melange = GCIOrganization(**group_properties)
  melange.put()

  group_properties.update({
    'scope_path': 'google/gsoc2009',
    'scope': gsoc2009,
    })

  role_properties.update({
      'key_name': 'google/gsoc2009/test',
      'link_id': 'test',
      'scope_path': 'google/gsoc2009',
      'scope': gsoc2009,
      'program': gsoc2009,
      'parent': current_user,
      })

  profile = GSoCProfile(**role_properties)
  role_properties.pop('parent')

  orgs = []
  for i in range(15):
    group_properties.update({
        'key_name': 'google/gsoc2009/org_%d' % i,
        'link_id': 'org_%d' % i,
        'name': 'Organization %d' % i,
        'short_name': 'Org %d' % i,
        'description': 'Organization %d!' % i,
        })

    entity = GSoCOrganization(**group_properties)
    orgs.append(entity)
    entity.put()

    # Admin (and thus mentor) for the first org
    if i == 0:
      profile.org_admin_for.append(entity.key())
      profile.mentor_for.append(entity.key())
      profile.is_mentor = True
      profile.is_org_admin = True
      profile.put()

    # Mentor for the second org
    if i == 1:
      profile.mentor_for.append(entity.key())
      profile.is_mentor = True
      profile.put()

  role_properties.update({
      'key_name': 'google/gci2009/test',
      'link_id': 'test',
      'scope_path': 'google/gci2009',
      'scope': gci2009,
      'program': gci2009,
      'org_admin_for': [melange.key()],
      'mentor_for': [melange.key()],
      'parent': current_user,
      })

  melange_admin = GCIProfile(**role_properties)
  # TODO: add GCI orgs
  melange_admin.put()

  task_properties = {
      'status': 'Open',
      'modified_by': melange_admin.key(),
      'subscribers': [melange_admin.key()],
      'title': 'Awesomeness',
      'created_by': melange_admin.key(),
      'created_on': now,
      'program': gci2009,
      'time_to_complete': 1337,
      'modified_on': now,
      'org': melange.key(),
      'description': '<p>AWESOME</p>',
      'difficulty_level': DifficultyLevel.MEDIUM,
      'types': ['Code']
  }

  gci_task = GCITask(**task_properties)
  gci_task.put()

  user_properties = {
      'key_name': 'student',
      'link_id': 'student',
      'account': users.User(email='student@example.com'),
      'name': 'Student',
      }

  student_user = User(**user_properties)
  student_user.put()

  student_id = 'student'
  student_properties = {
      'key_name': gsoc2009.key().name() + "/" + student_id,
      'link_id': student_id, 
      'scope_path': gsoc2009.key().name(),
      'parent': student_user,
      'scope': gsoc2009,
      'program': gsoc2009,
      'user': student_user,
      'is_student': True,
      'public_name': 'Student',
      'given_name': 'Student',
      'surname': 'Student',
      'birth_date': db.DateProperty.now(),
      'email': 'student@email.com',
      'im_handle': 'student_im_handle',
      'major': 'test major',
      'name_on_documents': 'Student',
      'res_country': 'United States',
      'res_city': 'city',
      'res_street': 'test street',
      'res_postalcode': '12345',
      'publish_location': True,
      'blog': 'http://www.blog.com/',
      'home_page': 'http://www.homepage.com/',
      'photo_url': 'http://www.photosite.com/thumbnail.png',
      'ship_state': None,
      'tshirt_size': 'XS',
      'tshirt_style': 'male',
      'degree': 'Undergraduate',
      'phone': '1650253000',
      'can_we_contact_you': True, 
      'program_knowledge': 'I heard about this program through a friend.'
      }

  melange_student = GSoCProfile(**student_properties)

  student_info_properties = {
      'key_name': melange_student.key().name(),
      'parent': melange_student,
      'expected_graduation': 2009,
      'program': gsoc2009,
      'school_country': 'United States',
      'school_name': 'Test School',
      'school_home_page': 'http://www.example.com',
      'program': gsoc2009,
  }
  student_info = GSoCStudentInfo(**student_info_properties)
  student_info.put()

  melange_student.student_info = student_info
  melange_student.put()

  user_properties = {
      'key_name': 'student2',
      'link_id': 'student2',
      'account': users.User(email='student@example.com'),
      'name': 'Student 2',
      }

  student_user2 = User(**user_properties)
  student_user2.put()
  student_id = 'student2'
  student_properties.update({
      'key_name': gsoc2009.key().name() + "/" + student_id,
      'link_id': student_id,
      'user': student_user2,
      'parent': student_user2,
  })

  melange_student2 = GSoCProfile(**student_properties)
  melange_student2.put()

  project_id = 'test_project'
  project_properties = {
      'key_name':  gsoc2009.key().name() + "/org_1/" + project_id,
      'link_id': project_id, 
      'scope_path': gsoc2009.key().name() + "/org_1",
      'scope': orgs[1].key(),

      'title': 'test project',
      'abstract': 'test abstract',
      'status': 'accepted',
      'student': melange_student,
      'mentor': profile,
      'program':  gsoc2009
       }

  melange_project = StudentProject(**project_properties)
  melange_project.put()
  student_info_properties.update({'number_of_projects': 1,
                                  'project_for_orgs': [orgs[1].key()]})
  student_info = GSoCStudentInfo(**student_info_properties)
  student_info.put()

  melange_student.student_info = student_info
  melange_student.put()

  project_id = 'test_project2'
  project_properties.update({
      'key_name':  gsoc2009.key().name() + "/org_1/" + project_id,
      'link_id': project_id,
      'student': melange_student2,
      'title': 'test project2'
      })
      
  student_info_properties.update({
      'key_name': gsoc2009.key().name() + "/" + student_id,
      'link_id': student_id,
      'parent': melange_student2,
  })
  student_info2 = GSoCStudentInfo(**student_info_properties)
  student_info2.put()

  melange_student2.student_info = student_info2
  melange_student2.put()

  melange_project2 = StudentProject(**project_properties)
  melange_project2.put()

  student_id = 'student'
  student_properties.update({
      'key_name': gci2009.key().name() + '/' + student_id,
      'parent': student_user,
      'scope': gci2009,
      'scope_path': gci2009.key().name(),
  })
  gci_student = GCIProfile(**student_properties)
  gci_student.put()

  student_info_properties.update({
      'key_name': gci_student.key().name(),
      'parent': gci_student,
      'program': gci2009,
  })
  student_info = GCIStudentInfo(**student_info_properties)
  student_info.put()
  gci_student.student_info = student_info
  gci_student.put()

  score_properties = {
      'parent': gci_student,
      'program': gci2009,
      'points': 5,
      'tasks': [gci_task.key()]
      }
  score = GCIScore(**score_properties)
  score.put()

  document_properties = {
      'key_name': 'site/site/home',
      'link_id': 'home',
      'scope_path': 'site',
      'scope': site,
      'prefix': 'site',
      'author': current_user,
      'title': 'Home Page',
      'short_name': 'Home',
      'content': 'This is the Home Page',
      'modified_by': current_user,
      }

  home_document = Document(**document_properties)
  home_document.put()


  document_properties = {
      'key_name': 'user/test/notes',
      'link_id': 'notes',
      'scope_path': 'test',
      'scope': current_user,
      'prefix': 'user',
      'author': current_user,
      'title': 'My Notes',
      'short_name': 'Notes',
      'content': 'These are my notes',
      'modified_by': current_user,
      }

  notes_document = Document(**document_properties)
  notes_document.put()

  site.home = home_document
  site.put()
  # pylint: disable=E1101
  memcache.flush_all()

  return http.HttpResponse('Done')

def clear(*args, **kwargs):
  """Removes all entities from the datastore.
  """

  # TODO(dbentley): If there are more than 1000 instances of any model,
  # this method will not clear all instances.  Instead, it should continually
  # call .all(), delete all those, and loop until .all() is empty.
  entities = itertools.chain(*[
      Notification.all(),
      GCIStudent.all(),
      Survey.all(),
      SurveyRecord.all(),
      StudentProposal.all(),
      GSoCOrganization.all(),
      GCIOrganization.all(),
      GSoCTimeline.all(),
      GCITimeline.all(),
      GSoCProgram.all(),
      GSoCProfile.all(),
      GCIProfile.all(),
      GSoCProposal.all(),
      GCIProgram.all(),
      GCIScore.all(),
      GSoCStudentInfo.all(),
      GCIStudentInfo.all(),
      GCITask.all(),
      Host.all(),
      Sponsor.all(),
      User.all(),
      Site.all(),
      Document.all(),
      ])

  try:
    for entity in entities:
      entity.delete()
  except db.Timeout:
    return http.HttpResponseRedirect('#')
  # pylint: disable=E1101
  memcache.flush_all()

  return http.HttpResponse('Done')


def reseed(*args, **kwargs):
  """Clears and seeds the datastore.
  """

  clear(*args, **kwargs)
  seed(*args, **kwargs)

  return http.HttpResponse('Done')
