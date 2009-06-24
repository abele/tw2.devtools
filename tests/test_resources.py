import webob as wo, webtest as wt, tw2.core as twc, tw2.tests, os, testapi

js = twc.JSLink(link='paj')
css = twc.CSSLink(link='joe')
jssrc = twc.JSSource(src='bob')

TestWidget = twc.Widget(template='genshi:tw2.tests.templates.inner_genshi', test='test')
html = "<html><head><title>a</title></head><body>hello</body></html>"

inject_widget = twc.Widget(id='a', template='b', resources=[js])

def simple_app(environ, start_response):
    req = wo.Request(environ)
    ct = 'text/html' if req.path == '/' else 'test/plain'
    resp = wo.Response(request=req, content_type="%s; charset=UTF8" % ct)
    inject_widget.req().prepare()
    resp.body = html
    return resp(environ, start_response)
mw = twc.TwMiddleware(simple_app)
tst_mw = wt.TestApp(mw)


class TestResources(object):
    def setUp(self):
        testapi.setup()

    def test_res_collection(self):
        wa = twc.Widget(id='a', template='b').req()
        wb = twc.Widget(id='b', template='b', resources=[js,css]).req()

        rl = testapi.request(1)
        wa.prepare()
        assert(len(rl.get('resources', [])) == 0)
        wb.prepare()
        for r in rl['resources']:
            assert(any(isinstance(r, b) for b in [js,css]))
        rl = testapi.request(2)
        assert(len(rl.get('resources', [])) == 0)

    def test_res_nodupe(self):
        wa = TestWidget(id='a', resources=[js]).req()
        wb = TestWidget(id='b', resources=[twc.JSLink(link='paj')]).req()
        wc = TestWidget(id='c', resources=[twc.JSLink(link='test')]).req()
        wd = TestWidget(id='d', resources=[css]).req()
        we = TestWidget(id='e', resources=[twc.CSSLink(link='joe')]).req()

        rl = testapi.request(1, mw)
        wa.display()
        wb.display()
        r = rl['resources']
        assert(len(rl['resources']) == 1)
        wc.display()
        assert(len(rl['resources']) == 2)
        wd.display()
        we.display()
        assert(len(rl['resources']) == 3)


    #--
    # ResourcesApp
    #--
    def test_not_found(self):
        #assert(tst_mw.get('/fred', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/test', expect_errors=True).status == '404 Not Found')

    def test_serve(self):
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        fcont = open(os.path.join(os.path.dirname(tw2.tests.__file__), 'templates/simple_genshi.html')).read()
        assert(tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body == fcont)
        assert(tst_mw.get('/resources/tw2.tests/templates/notexist', expect_errors=True).status == '404 Not Found')

    def test_dir_traversal(self): # check for potential security flaw
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        assert(tst_mw.get('/resources/tw2.tests/__init__.py', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/tw2.tests/templates/../__init__.py', expect_errors=True).status == '404 Not Found')

    def test_different_file(self):
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        assert(tst_mw.get('/resources/tw2.tests/simple_kid.kid', expect_errors=True).status == '404 Not Found')

    def test_zipped(self):
        # assumes webtest is installed as a zipped egg
        mw.resources.register('webtest', '__init__.py')
        assert(tst_mw.get('/resources/webtest/__init__.py').body.startswith('# (c) 2005 Ian'))

    #--
    # Links register resources
    #--
    def test_link_reg(self):
        testapi.request(1, mw)
        wa = twc.JSLink(modname='tw2.tests', filename='templates/simple_mako.mak').req()
        wa.prepare()
        assert(wa.link == '/resources/tw2.tests/templates/simple_mako.mak')
        tst_mw.get(wa.link)

    def test_mime_type(self):
        testapi.request(1, mw)
        wa = twc.JSLink(modname='tw2.tests', filename='templates/simple_genshi.html').req()
        wa.prepare()
        resp = tst_mw.get(wa.link)
        assert(resp.content_type == 'text/html')
        assert(resp.charset == 'UTF-8')

    #--
    # Resource injector
    #--
    def test_inject_head(self):
        rl = testapi.request(1, mw)
        out = twc.inject_resources(html, [js.req()])
        assert(out == '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello</body></html>')

    def test_inject_body(self):
        rl = testapi.request(1, mw)
        out = twc.inject_resources(html, [jssrc.req()])
        assert(out == '<html><head><title>a</title></head><body>hello<script type="text/javascript">bob</script></body></html>')

    def test_inject_both(self):
        rl = testapi.request(1, mw)
        out = twc.inject_resources(html, [js.req(), jssrc.req()])
        assert(out == '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello<script type="text/javascript">bob</script></body></html>')

    def test_detect_clear(self):
        widget = twc.Widget(id='a', template='genshi:tw2.tests.templates.inner_genshi', test='test', resources=[js])
        rl = testapi.request(1, mw)
        assert(len(rl.get('resources', [])) == 0)
        widget.display()
        assert(len(rl.get('resources', [])) == 1)
        out = twc.inject_resources(html)
        assert(len(rl.get('resources', [])) == 0)

    #--
    # General middleware
    #--
    def test_mw_resourcesapp(self):
        testapi.request(1)
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        fcont = open(os.path.join(os.path.dirname(tw2.tests.__file__), 'templates/simple_genshi.html')).read()
        print tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body
        assert(tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body == fcont)

    def test_mw_clear_rl(self):
        rl = testapi.request(1)
        rl['blah'] = 'lah'
        tst_mw.get('/')
        assert(rl == {})

    def test_mw_inject(self):
        testapi.request(1, mw)
        TestWidget(id='a', resources=[js]).display()
        assert(tst_mw.get('/').body == '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello</body></html>')

    def test_mw_inject_html_only(self):
        testapi.request(1, mw)
        TestWidget(id='a', resources=[js]).display()
        assert(tst_mw.get('/plain').body == html)

