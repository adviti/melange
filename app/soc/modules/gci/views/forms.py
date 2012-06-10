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

"""Module containing the boiler plate required to construct templates
"""


import itertools
import re

from google.appengine.ext import db

from django.core.urlresolvers import reverse
from django.utils.datastructures import MergeDict
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.template import defaultfilters
from django.utils.formats import dateformat

from soc.views import forms
from soc.views import org_app


AVATAR_LOWER_BOUND = 1
AVATAR_UPPER_BOUND = 26
AVATAR_DEFAULT_COLOR = 'blue'
RE_AVATAR_COLOR = re.compile(r'(\d\d?)-(\w+)\.jpg$')
TEMPLATE_PATH = 'v2/modules/gci/_form.html'

# The standard input fields should be available to all importing modules
CharField = forms.CharField
CheckboxInput = forms.CheckboxInput
CheckboxSelectMultiple = forms.CheckboxSelectMultiple
DateInput = forms.DateInput
DateTimeInput = forms.DateTimeInput
FileInput = forms.FileInput
HiddenInput = forms.HiddenInput
RadioSelect = forms.RadioSelect
Select = forms.Select
SelectMultiple = forms.SelectMultiple
TextInput = forms.TextInput
Textarea = forms.Textarea

# The standard error classes should be available to all importing modules
ValidationError = forms.ValidationError


class AvatarWidget(HiddenInput):
  """The rendering customization to be used for avatar.
  """

  def __init__(self, attrs=None, avatars=(), colors=()):
    super(AvatarWidget, self).__init__(attrs=attrs)
    self.avatars = avatars
    self.colors = colors

  def render(self, name, value, attrs={}):
    # make sure value is basestring instance
    if not isinstance(value, basestring):
      value = ''

    # determine the right value
    match = RE_AVATAR_COLOR.match(value)
    if not match:
      value = '%d-%s.jpg' % (AVATAR_LOWER_BOUND, AVATAR_DEFAULT_COLOR)
      color = AVATAR_DEFAULT_COLOR
    else:
      number, color = match.groups()
      number = int(number)
      if number < AVATAR_LOWER_BOUND or number > AVATAR_UPPER_BOUND:
        number = AVATAR_LOWER_BOUND
      if color not in self.colors:
        color = AVATAR_DEFAULT_COLOR
      value = '%d-%s.jpg' % (number, color)

    # the returned avatar in partial html
    output = []

    # preview
    output.append(self._renderPreview(value))

    # picker container
    output.append('<div id="avatar-picker-container">')

    # avatar picker
    output.append(self._renderPicker('avatar-icon', value, self.avatars[color]))

    # color picker
    output.append(self._renderPicker('avatar-color', color, self.colors))

    # hidden value
    w = HiddenInput(attrs=attrs)
    attrs['value'] = value
    w_html = w.render(name, value, attrs=attrs)
    output.append(w_html)

    # close the picker container
    output.append('</div>')

    return mark_safe(u'\n'.join(output))

  def _renderPreview(self, value):
    return mark_safe(
        '<div id="avatar-preview-container"><img id="avatar-preview" '
        'src="%s" width="80" height="80"></div>' % value)

  def _renderPicker(self, name, value, choices=()):
    options = [(i, i) for i in choices]
    picker = Select(choices=options)
    picker_html = picker.render(name, value, attrs={'id': name})

    return mark_safe('<div id="%s-picker">%s</div>' % (name, picker_html))


class MultipleSelectWidget(Select):
  """Extends the Django's Select widget to have multiple dynamic select widgets.
  """

  def __init__(self, attrs=None, choices=(), disabled_option=()):
    super(MultipleSelectWidget, self).__init__(attrs, choices)
    self.disabled_option = disabled_option

  def render(self, name, values, attrs=None, choices=()):
    final_attrs = self.build_attrs(attrs)

    if not values: values = ['']
    wrapper_id = final_attrs.pop('wrapper_id', 'multiple-select-wrapper')
    output = [u'<div id="%s">' % (wrapper_id)]

    add_new_text = final_attrs.pop('add_new_text', 'add another select widget')

    for i, value in enumerate(values):
      select_id = final_attrs.pop('select_id', 'select-field')
      attr_dict = {
          'id': '%s-%d' % (select_id, i)
          }
      output.append(super(MultipleSelectWidget, self).render(
          name, value, attr_dict, choices=choices))

    output.append(u'</div>')
    output.append(u'<div class="add-field-link clearfix">')
    output.append(u'<a href="javascript:new_link()">+ %s</a>' % (add_new_text))
    output.append(u'</div>')

    return mark_safe(u'\n'.join(output))

  def value_from_datadict(self, data, files, name):
    """Given a dictionary of data and this widget's name, returns the value
    of this widget. Returns None if it's not provided.
    """
    if isinstance(data, (MultiValueDict, MergeDict)):
      return data.getlist(name)
    return data.get(name, None)

  def render_options(self, choices, selected_choices):
    output = []
    if self.disabled_option:
      disabled_value, disabled_label = self.disabled_option
      output.append(u'<option value="%s" disabled=disabled>%s</option>' % (
          escape(disabled_value),
          conditional_escape(force_unicode(disabled_label))))

    output.append(super(MultipleSelectWidget, self).render_options(
        choices, selected_choices))

    return u'\n'.join(output)

class RadioInput(forms.RadioInput):
  """The rendering customization to be used for individual radio elements.
  """

  def __unicode__(self):
    if 'id' in self.attrs:
      label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
    else:
      label_for = ''
    choice_label = conditional_escape(force_unicode(self.choice_label))
    return mark_safe(
        u'%s <label%s>%s</label>' % (
        self.tag(), label_for, choice_label))


class RadioFieldRenderer(forms.RadioFieldRenderer):
  """The rendering customization to use the Uniform CSS on radio fields.
  """

  def __iter__(self):
    for i, choice in enumerate(self.choices):
      yield RadioInput(self.name, self.value, self.attrs.copy(), choice, i)

  def render(self):
    """Outputs the enclosing <div> for this set of radio fields.
    """
    return mark_safe(u'<div class="form-radio">%s</div>' % u'\n'.join([
        u'<div id="form-row-radio-%s" class="form-radio-item">%s</div>'
        % (w.attrs.get('id', ''), force_unicode(w)) for w in self]))


class CheckboxSelectMultiple(CheckboxSelectMultiple):
  def render(self, name, value, attrs=None, choices=()):
    if value is None:
      value = []
    has_id = attrs and 'id' in attrs
    final_attrs = self.build_attrs(attrs, name=name)
    output = [u'<div class="form-checkbox">']
    # Normalize to strings
    str_values = set([force_unicode(v) for v in value])
    for i, (option_value, option_label) in enumerate(
        itertools.chain(self.choices, choices)):
      # If an ID attribute was given, add a numeric index as a suffix,
      # so that the checkboxes don't all have the same ID attribute.
      if has_id:
        final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
        label_for = u' for="%s"' % final_attrs['id']
      else:
        label_for = ''

      cb = forms.CheckboxInput(
          final_attrs, check_test=lambda value: value in str_values)
      option_value = force_unicode(option_value)
      rendered_cb = cb.render(name, option_value)
      option_label = conditional_escape(force_unicode(option_label))
      output.append(
          u'<div id="form-row-checkbox-%s" class="form-checkbox-item">'
          '%s<label%s>%s</label></div>' % (
          final_attrs['id'], rendered_cb, label_for, option_label))
    output.append(u'</div>')
    return mark_safe(u'\n'.join(output))


class GCIModelForm(forms.ModelForm):
  """Django ModelForm class which uses our implementation of BoundField.
  """
  
  def __init__(self, *args, **kwargs):
    super(GCIModelForm, self).__init__(
        GCIBoundField, *args, **kwargs)

  def templatePath(self):
    return TEMPLATE_PATH


class OrgAppEditForm(org_app.OrgAppEditForm):
  """Form to create/edit GCI organization application survey.
  """

  class Meta(org_app.OrgAppEditForm.Meta):
    pass

  def __init__(self, *args, **kwargs):
    super(OrgAppEditForm, self).__init__(
        GCIBoundField, *args, **kwargs)

  def templatePath(self):
    return TEMPLATE_PATH


class OrgAppTakeForm(org_app.OrgAppTakeForm):
  """Form for would-be organization admins to apply for a GCI program.
  """

  CHECKBOX_SELECT_MULTIPLE = CheckboxSelectMultiple

  RADIO_FIELD_RENDERER = RadioFieldRenderer

  class Meta(org_app.OrgAppTakeForm.Meta):
    pass

  def __init__(self, survey, tos_content, *args, **kwargs):
    super(OrgAppTakeForm, self).__init__(
        survey, tos_content, GCIBoundField, *args, **kwargs)

  def templatePath(self):
    return TEMPLATE_PATH


class GCIBoundField(forms.BoundField):
  """GCI specific BoundField representation.
  """

  def __init__(self, form, field, name):
    super(GCIBoundField, self).__init__(form, field, name)

  def render(self):
    widget = self.field.widget

    if isinstance(widget, forms.DocumentWidget):
      self.setDocumentWidgetHelpText()

    if isinstance(widget, forms.ReferenceWidget):
      return self.renderReferenceWidget()
    elif isinstance(widget, forms.TOSWidget):
      return self.renderTOSWidget()
    elif isinstance(widget, forms.RadioSelect):
      return self.renderRadioSelect()
    elif isinstance(widget, forms.CheckboxSelectMultiple):
      return self.renderCheckSelectMultiple()
    elif isinstance(widget, forms.TextInput):
      return self.renderTextInput()
    elif isinstance(widget, forms.DateInput):
      return self.renderTextInput()
    elif isinstance(widget, forms.Select):
      return self.renderSelect()
    elif isinstance(widget, forms.CheckboxInput):
      return self.renderCheckboxInput()
    elif isinstance(widget, forms.Textarea):
      return self.renderTextArea()
    elif isinstance(widget, forms.DateTimeInput):
      return self.renderTextInput()
    elif isinstance(widget, forms.HiddenInput):
      return self.renderHiddenInput()
    elif isinstance(widget, forms.FileInput):
      return self.renderFileInput()

    return self.NOT_SUPPORTED_MSG_FMT % (
        widget.__class__.__name__)

  def renderTextInput(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        }

    return mark_safe('%s%s%s' % (
        self._render_label(),
        self.as_widget(attrs=attrs),
        self._render_note(),
    ))

  def renderCheckboxInput(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        'style': 'opacity: 100;',
        }

    return mark_safe(
        '<label>%s%s%s%s</label>%s' % (
        self.as_widget(attrs=attrs),
        self.field.label,
        self._render_is_required(),
        self._render_error(),
        self._render_note(),
        ))

  def renderTextArea(self):
    attrs = {
        'id': 'melange-%s-textarea%s' % (self.name, self.idSuffix(self)),
        'class': 'textarea'
        }

    return mark_safe('%s%s%s' % (
        self._render_label(),
        self.as_widget(attrs=attrs),
        self._render_note(),
    ))

  def renderReferenceWidget(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        'name': self.name,
        'type': "hidden",
        'class': 'text',
        }

    hidden = self.as_widget(attrs=attrs)
    original = self.form.initial.get(self.name)

    key = self.form.initial.get(self.name)

    if key:
      entity = db.get(key)
      if entity:
        self.form.initial[self.name] = entity.key().name()

    attrs = {
        'id': self.name + "-pretty" + self.idSuffix(self),
        'name': self.name + "-pretty",
        'class': 'text',
        }
    pretty = self.as_widget(attrs=attrs)
    self.form.initial[self.name] = original

    return mark_safe('%s%s%s%s' % (
        self._render_label(),
        pretty,
        hidden,
        self._render_note(),
    ))

  def renderSelect(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        'style': 'opacity: 100;',
        }

    return mark_safe('%s%s%s%s' % (
        self.as_widget(attrs=attrs),
        self._render_is_required(),
        self._render_error(),
        self._render_note(),
    ))

  def renderTOSWidget(self):
    checkbox_attrs = {
        'id': self.name + self.idSuffix(self),
        'style': 'opacity: 100;',
        }

    return mark_safe(
        '<label>%s%s%s%s</label>%s' % (
        self.as_widget(attrs=checkbox_attrs),
        self.field.label,
        self._render_is_required(),
        self._render_error(),
        self._render_note(),
        ))

  def renderHiddenInput(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        'name': self.name,
        'type': 'hidden',
        'value': self.field.initial or '',
        }
    return self.as_widget(attrs=attrs)

  def renderFileInput(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        }

    current_file_fmt = """
        <br/>
        <p>
        File: <a href="%(link)s">%(name)s</a><br/>
        Size: %(size)s <br/>
        Uploaded on: %(uploaded)s UTC
        <p>
    """

    current_file = current_file_fmt % {
        'name': self.field._file.filename,
        'link': self.field._link,
        'size': defaultfilters.filesizeformat(self.field._file.size),
        'uploaded': dateformat.format(
              self.field._file.creation, 'M jS Y, h:i:sA'),
    } if getattr(self.field, '_file', False) else ""

    return mark_safe('%s%s%s%s' % (
        self._render_label(),
        self.as_widget(attrs=attrs),
        self._render_note(),
        current_file,
    ))

  def renderRadioSelect(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        }

    return mark_safe('%s%s%s' % (
        self._render_label(),
        self.as_widget(attrs=attrs),
        self._render_note(),
    ))

  def renderCheckSelectMultiple(self):
    attrs = {
        'id': self.name + self.idSuffix(self),
        }

    return mark_safe('%s%s%s' % (
        self._render_label(),
        self._render_note(),
        self.as_widget(attrs=attrs),
    ))

  def setDocumentWidgetHelpText(self):
    value = self.form.initial.get(self.name, self.field.initial)

    if value:
      document = db.get(value)
      sponsor, program = document.scope_path.split('/')
      args = [document.prefix, sponsor, program, document.link_id]
    else:
      scope_path = self.form.request_data.program.key().id_or_name()
      sponsor, program = scope_path.split('/')
      args = ['gci_program', sponsor, program, self.name]

    edit_document_link = reverse('edit_gci_document', args=args)
    self.help_text = """<a href="%s">Click here to edit this document.</a>
        <br />%s""" % (edit_document_link, self.help_text)

  def _render_label(self):
    return '<label class="form-label">%s%s%s</label>' % (
        self.field.label,
        self._render_is_required(),
        self._render_error(),
    ) if self.field.label else ''

  def _render_is_required(self):
    return '<em>*</em>' if self.field.required else ''

  def _render_error(self):
    if not self.errors:
      return ''

    return '<span class="form-row-error-msg">%s</span>' % (
        self.errors[0])

  def _render_note(self, note=None):
    return '<span class="note">%s</span>' % (
        note if note else self.help_text)

  def div_class(self):
    prefix = getattr(self.form.Meta, 'css_prefix', None)
    name = prefix + '-' + self.name if prefix else self.name

    widget_div_class = self.field.widget.attrs.get('div_class', None)
    if widget_div_class:
      name = '%s %s' % (widget_div_class, name)

    if self.errors:
      name += ' error'
    return name
