import cgi, random, sys, urllib
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app

selectJs = """
<script language="JavaScript" type="text/javascript">
<!--
	function select_text()
	{
		el = document.getElementById('url');
		if (el.createTextRange) 
		{
			var oRange = el.createTextRange();
	   		oRange.moveStart("character", 0);
			oRange.moveEnd("character", el.value.length);
			oRange.select();
		}
		else if (el.setSelectionRange) 
		{
			el.setSelectionRange(0, el.value.length);
		}
		el.focus();
	}

	function PageInit() {
		select_text();
	}
        window.onload = PageInit;
//-->
</script>
"""

dickRules = (
  "~*@=*8",
  "@=*8",
  "8=*D~*",
  "8=*D",
  "mydi*ckishu*ge",
  "myco*ckishu*ge",
)

def get_server(request):
  server, port = request.server_name, request.server_port
  address =  "http://" + server
  if int(port) != 80:
    address += ":%s" % port
  return address + "/"

def header(request):
  html = "<html><head><title>100% All-natural URL enhancement!</title></head><body>" + selectJs + """
    <div style="width:400px;margin:0 auto;align:center;">
      <a href="/"><img src="http://wxbanker.org/dicks/logo.png" align="center" border="0"/></a><br/>"""
  return html

def footer():
  return """</div></body></html>"""

class UrlMap(db.Model):
  enhancedPhrase = db.StringProperty()
  destinationUrl = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  hits = db.IntegerProperty()

class MainPage(webapp.RequestHandler):
  def get(self):
    response = """
      <form action="/enhance" method="post">
        <div><textarea name="content" rows="3" cols="60"></textarea></div>
        <div><input type="submit" value="Enhance that embarrassing URL!"></div>
      </form>"""
    self.response.out.write(header(self.request) + response + footer())

class Reporter(webapp.RequestHandler):
  def get(self):
    urls = db.GqlQuery("SELECT * FROM UrlMap")
    response = "<ul>"
    for url in urls:
      response += "<li>%s => %s (%i)</li>" % (url.enhancedPhrase, url.destinationUrl, url.hits)
    response += "</ul>"
    self.response.out.write(header(self.request) + response + footer())

class Enhancer(webapp.RequestHandler):
  def generatePhrase(self):
    from emoji import characters
    phrase = ""
    for i in range(0,4):
      phrase += characters[random.randrange(0, len(characters))]
    
#    phrase = "8------D-" + str(random.randint(1,sys.maxint))
    return phrase

  def generateUrl(self, phrase):
    return get_server(self.request) + phrase

  def post(self):
    mapObj = UrlMap()
    mapObj.destinationUrl = self.request.get('content')
    phrase = self.generatePhrase()
    mapObj.enhancedPhrase = urllib.quote(phrase.encode('utf-8'))
    mapObj.hits = 0
    mapObj.put()

    newUrl = self.generateUrl(phrase)

    
    response = 'Wow, we\'re not really sure how you had friends with such an insignificant URL!</br>'
    response += '<br/>We highly recommend not showing that to anyone, instead use:<br/><br/>'
    response += '</div><center><input type="text" value="'+newUrl+'" size="60" id="url"/><div><br/>Sorry this URL is so lame, an actual enhancing algorithm is coming soon.'
    self.response.out.write(header(self.request) + response + footer())

class Char(webapp.RequestHandler):
  def get(self):
    from emoji import characters
    output = "<div style='font-size: 72pt'>"
    for n in range(0, len(characters), 5):
      output += characters[n:n+5] + "<br />"
    output += "</div>"
    
    self.response.out.write(header(self.request) + output + footer())

class Redirecter(webapp.RequestHandler):
  def get(self):
    key = self.request.url.split('/')[-1]
    try:
      url = db.GqlQuery("SELECT * FROM UrlMap WHERE enhancedPhrase = :1 LIMIT 1", key)[0]
    except IndexError:
      self.response.out.write(header(self.request) + "Sorry friends, no dice on that one (%s)."%key + footer())
    else:
      url.hits += 1
      url.put()
      dest = url.destinationUrl
      if not dest.startswith("http"):
        dest = "http://" + dest
      self.redirect(dest)

application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/enhance', Enhancer),
   ('/tellmeallaboutdicks', Reporter),
   ('/char', Char),
   ('/.*', Redirecter)
   ],
  debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()