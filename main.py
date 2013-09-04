#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import webapp2
import jinja2
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import os
import urllib
import logging

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('index.html')
    self.response.write(template.render())
    

class UploadedFile(ndb.Model):
  title = ndb.StringProperty(required=True)
  artist = ndb.StringProperty(required=True)
  album = ndb.StringProperty(required=False)
  genre = ndb.StringProperty(required=False, repeated=True)
  audio_key = ndb.BlobKeyProperty()

class Profile(ndb.Model):
  firstname = ndb.StringProperty(required=True)
  lastname = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
  publish_name = ndb.StringProperty(required=True)
  password = ndb.StringProperty(required=True)
  songs = ndb.KeyProperty(kind=UploadedFile, repeated=True)

class UploadFormHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/uploading')
    template = jinja_environment.get_template('upload.html')
    self.response.write(template.render({'upload_url':upload_url}))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    title = self.request.get('title')
    artist = self.request.get('artist')
    album = self.request.get('album', default_value=None)
    genre = self.request.get_all('genre', default_value=None)
    upload_files = self.get_uploads()  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    uploaded_track = UploadedFile(title=title, artist=artist, album=album, genre=genre, audio_key=blob_info.key())
    uploaded_track.put()
    self.redirect('/upload_success')

class UploadSuccessHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('upload_success.html')
    self.response.write(template.render({}))

class LibraryHandler(webapp2.RequestHandler):
  def get(self):
    songs = UploadedFile.query()
    logging.info(type(songs))
    logging.info(songs)
    songs = songs.order(UploadedFile.title)
    template_values = {'songs' : songs}
    template = jinja_environment.get_template('library.html')
    self.response.write(template.render(template_values))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)
    
class RecordHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('recording.html')
    self.response.write(template.render())

class OtherHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('error.html')
    self.response.write(template.render())

class FeatureHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('features-main.html')
    self.response.write(template.render())

class AboutHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('aboutus.html')
    self.response.write(template.render())

class PianoHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('piano.html')
    self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/upload', UploadFormHandler),
    ('/uploading', UploadHandler),
    ('/upload_success', UploadSuccessHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/library', LibraryHandler),
    ('/record', RecordHandler),
    ('/features', FeatureHandler),
    ('/aboutus', AboutHandler),
    ('/piano', PianoHandler),
    ('/.*', MainHandler),
], debug=True)
