# Copyright 2012 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing the Students Info view for the admin.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation
from soc.views.helper import lists
from soc.views.template import Template
from soc.views.helper import url_patterns

from soc.modules.gci.models.profile import GCIStudentInfo
from soc.modules.gci.models.score import GCIScore
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper.url_patterns import url
from soc.modules.gci.views.helper import url_names


def addAddressColumns(list_config):
  """Adds address columns to the specified list config.

  Columns added:
    * res_street
    * res_street_extra
    * res_city
    * res_state
    * res_country
    * res_postalcode
    * phone
    * ship_name
    * ship_street
    * ship_street_extra
    * ship_city
    * ship_state
    * ship_country
    * ship_postalcode
    * tshirt_style
    * tshirt_size
  """
  list_config.addColumn('res_street', 'Street',
      (lambda e, sp, *args: sp[e.parent_key()].res_street), hidden=True)
  list_config.addColumn('res_street_extra', 'Street Extra', 
      (lambda e, sp, *args: sp[e.parent_key()].res_street_extra), hidden=True)
  list_config.addColumn('res_city', 'City',
      (lambda e, sp, *args: sp[e.parent_key()].res_city), hidden=True)
  list_config.addColumn('res_state', 'State',
      (lambda e, sp, *args: sp[e.parent_key()].res_state), hidden=True)
  list_config.addColumn('res_country', 'Country',
      (lambda e, sp, *args: sp[e.parent_key()].res_country), hidden=True)
  list_config.addColumn('res_postalcode', 'Postalcode',
      (lambda e, sp, *args: sp[e.parent_key()].res_postalcode), hidden=True)
  list_config.addColumn('phone', 'Phone',
      (lambda e, sp, *args: sp[e.parent_key()].phone), hidden=True)
  list_config.addColumn('ship_name', 'Ship Name',
      (lambda e, sp, *args: sp[e.parent_key()].shipping_name()), hidden=True)
  list_config.addColumn('ship_street', 'Ship Street',
      (lambda e, sp, *args: sp[e.parent_key()].shipping_street()), hidden=True)
  list_config.addColumn('ship_street_extra', 'Ship Street Extra',
      (lambda e, sp, *args: sp[e.parent_key()].shipping_street_extra()), 
      hidden=True)
  list_config.addColumn('ship_city', 'Ship City',
      (lambda e, sp, *args: sp[e.parent_key()].shipping_city()), hidden=True)
  list_config.addColumn('ship_state', 'Ship State', 
      (lambda e, sp, *args: sp[e.parent_key()].shipping_state()), hidden=True)
  list_config.addColumn('ship_country', 'Ship Country',
      (lambda e, sp, *args: sp[e.parent_key()].shipping_country()), hidden=True)
  list_config.addColumn('ship_postalcode', 'Ship Postalcode',
      (lambda e, sp, *args: sp[e.parent_key()].shipping_postalcode()), 
      hidden=True)
  list_config.addColumn('tshirt_style', 'T-Shirt Style',
      (lambda e, sp, *args: sp[e.parent_key()].tshirt_style), hidden=True)
  list_config.addColumn('tshirt_size', 'T-Shirt Size',
      (lambda e, sp, *args: sp[e.parent_key()].tshirt_size), hidden=True)
 
 
class StudentsList(Template):
  """Component for listing all the students in GCI.
  """
  
  def __init__(self, request, data):
    self.data = data
    self.request = request
    self.idx = 1
    
    list_config = lists.ListConfiguration()
    list_config.addColumn(
        'name', 'Name', lambda e, sp, *args: sp[e.parent_key()].name())
    list_config.addColumn(
        'link_id', 'Link ID', lambda e, sp, *args: sp[e.parent_key()].link_id)
    list_config.addColumn(
        'email', 'Email', lambda e, sp, *args: sp[e.parent_key()].email)
    list_config.addColumn('given_name', 'Given name', 
        (lambda e, sp, *args: sp[e.parent_key()].given_name), hidden=True)
    list_config.addColumn('surname', 'Surname', 
        (lambda e, sp, *args: sp[e.parent_key()].surname), hidden=True)
    list_config.addColumn('name_on_documents', 'Legal name', 
        (lambda e, sp, *args: sp[e.parent_key()].name_on_documents),
        hidden=True)
    list_config.addColumn(
        'birth_date', 'Birthdate',
        (lambda e, sp, *args: sp[e.parent_key()].birth_date.strftime(
        "%B %d, %Y")), hidden=True)
   
    addAddressColumns(list_config)
   
    list_config.addColumn('school_name', 'School name',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.school_name), 
        hidden=True)
    list_config.addColumn('school_country', 'School Country',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.school_country), 
        hidden=True)
    list_config.addColumn('school_type', 'School Type',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.school_type), 
        hidden=True)
    list_config.addColumn('major', 'Major',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.major), 
        hidden=True)
    list_config.addColumn('degree', 'Degree',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.degree), 
        hidden=True)
    list_config.addColumn('grade', 'Grade',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.grade),
        hidden=True)
    list_config.addColumn('expected_graduation', 'Expected Graduation',
        (lambda e, sp, *args: sp[e.parent_key()].student_info.expected_graduation), 
        hidden=True)
   
    list_config.addSimpleColumn('points', 'Points')
    list_config.addColumn(
        'no_of_tasks_completed', 'No of completed tasks',
        (lambda e, *args: len(e.tasks)))
   
    def formsSubmitted(e, sp, form):
      """Returns "Yes" if form has been submitted otherwise "No".
     
      form takes either 'consent' or 'student_id' as values which stand
      for parental consent form and student id form respectively.
      """
      info = sp[e.parent_key()].student_info
      if form == 'consent':
        consent = GCIStudentInfo.consent_form.get_value_for_datastore(info)
        if consent:
          return 'Yes'
      if form == 'student_id':
        student_id = GCIStudentInfo.student_id_form.get_value_for_datastore(info)
        if student_id:
          return 'Yes'
      return 'No'
     
    list_config.addColumn(
        'consent_form', 'Consent Form Submitted',
        (lambda e, sp, *args: formsSubmitted(e, sp, 'consent')))
    list_config.addColumn(
        'student_id_form', 'Student ID Form Submitted',
        (lambda e, sp, *args: formsSubmitted(e, sp, 'student_id')))
   
    self._list_config = list_config

  def getListData(self):
    idx = lists.getListIndex(self.request)

    if idx != self.idx:
      return None

    q = GCIScore.all()

    q.filter('program', self.data.program)

    starter = lists.keyStarter

    def prefetcher(entities):
      keys = []

      for entity in entities:
        key = entity.parent_key()
        if key:
          keys.append(key)
      
      entities = db.get(keys)
      sp = dict((i.key(), i) for i in entities if i)

      return ([sp], {})

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter, prefetcher=prefetcher)

    return response_builder.build()

  def templatePath(self):
    return'v2/modules/gci/students_info/_students_list.html'
 
  def context(self):
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx)

    return {
        'name': 'students',
        'title': 'Participating students',
        'lists': [list],
        'description': ugettext(
            'List of participating students'),
    }

class StudentsInfoPage(RequestHandler):
  """View for the students info page for the admin.
  """

  def templatePath(self):
    return 'v2/modules/gci/students_info/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'admin/students_info/%s$' % url_patterns.PROGRAM, self,
            name=url_names.GCI_STUDENTS_INFO),
    ]

  def checkAccess(self):
    self.check.isHost()

  def jsonContext(self):
    list_content = StudentsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    return {
        'page_name': "List of Students for %s" % self.data.program.name,
        'students_info_list': StudentsList(self.request, self.data),
    }
