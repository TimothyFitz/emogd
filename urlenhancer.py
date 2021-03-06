import cgi, random, sys, urllib, os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template



def get_server(request):
  server, port = request.server_name, request.server_port
  if 'emo.gd' in server:
    server = 'emo.gd'
  address =  "http://" + server
  if int(port) != 80:
    address += ":%s" % port
  return address + "/"

def templatize(response):
  template_values = {"response": response}
  return template.render('template.html', template_values)
    
class UrlMap(db.Model):
  enhancedPhrase = db.StringProperty()
  destinationUrl = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  hits = db.IntegerProperty()
  emojiedUrl = db.StringProperty()

class MainPage(webapp.RequestHandler):
  def get(self):
    response = ("""Emojied: a URL shortener that takes your URL and gives you
    back an emojied URL <div class="iphonehide">(shows up rad on the iPhone)</div><br/><br/>""")
    response += """
      <form action="/emojied" method="post">
        <div><input type="text" size="30" name="content"/></div>
        <div><input type="submit" value="Emojify!"></div>
      </form>"""
    self.response.out.write(templatize(response))

class Reporter(webapp.RequestHandler):
  def get(self):
    urls = db.GqlQuery("SELECT * FROM UrlMap")
    response = "<ul>"
    for url in urls:
      response += "<li>%s => \'%s\' (%i)</li>" % (url.enhancedPhrase, url.destinationUrl, url.hits)
    response += "</ul>"
    self.response.out.write(templatize(response))

class Enhancer(webapp.RequestHandler):
  def generatePhrase(self):
    from emoji import characters
    phrase = ""
    for i in range(0,4):
      phrase += characters[random.randrange(0, len(characters))]

    return phrase

  def generateUrl(self, phrase):
    return get_server(self.request) + phrase

  def post(self):
    content = self.request.get('content')
    newUrl = ''
    try:
        existing = db.GqlQuery("SELECT * FROM UrlMap WHERE destinationUrl = :1", content)[0]
        if(existing.emojiedUrl):
            newUrl = existing.emojiedUrl    

    except IndexError:
        mapObj = UrlMap()
        mapObj.destinationUrl = content
        phrase = self.generatePhrase()
        mapObj.enhancedPhrase = urllib.quote(phrase.encode('utf-8'))
        mapObj.hits = 0

        newUrl = self.generateUrl(phrase)

        mapObj.emojiedUrl = newUrl
        mapObj.put()

    response = 'Here\'s your emojied URL:<br/>' 
    response += '</div><center><input type="text" value="'+newUrl+'" size="30" id="url"/><div>'
    self.response.out.write(templatize(response))

class Char(webapp.RequestHandler):
  def get(self):
    from emoji import characters
    output = "<div style='font-size: 72pt'>"
    for n in range(0, len(characters), 5):
      output += characters[n:n+5] + "<br />"
    output += "</div>"
    self.response.out.write(templatize(response))

class Redirecter(webapp.RequestHandler):
  def get(self):
    key = self.request.url.split('/')[-1]
    try:
      url = db.GqlQuery("SELECT * FROM UrlMap WHERE enhancedPhrase = :1 LIMIT 1", key)[0]
    except IndexError:
      from emoji import characters
      response = ("Emoji fail. Please <a href=\"/\">emoje something else "+
        characters[47]+"</a>")
      self.response.out.write(templatize(response))
    else:
      url.hits += 1
      url.put()
      dest = url.destinationUrl
      if not dest.startswith("http"):
        dest = "http://" + dest
      self.redirect(dest)

application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/emojied', Enhancer),
   ('/tellmeallaboutemojied', Reporter),
   ('/char', Char),
   ('/.*', Redirecter)
   ],
  debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
