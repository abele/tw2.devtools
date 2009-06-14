import tw.core as twc, testapi

class TestHierarchy(object):
    def setUp(self):
        testapi.setup()

    #--
    # Compound IDs
    #--
    def test_compound_id(self):
        test = twc.CompoundWidget.cls(id='x', children=[
            twc.Widget.cls(id='a'),
            twc.Widget.cls(id='b'),
        ])
        assert(test.children.a._compound_id() == 'x:a')

    def test_invalid_id(self):
        try:
            a = twc.Widget.cls(id=':')
            assert(False)
        except twc.ParameterError, e:
            assert(str(e) == "Not a valid identifier: ':'")

    def test_id_none(self):
        test = twc.Widget.cls(id=None)
        assert(test._compound_id() == '')

    def test_repeating_id(self):
        test = twc.RepeatingWidget.cls(id='x', child=twc.Widget)
        assert(test.children[3]._compound_id() == 'x:3')

    #--
    # CompoundWidget / WidgetBunch
    #--
    def test_widgetbunch(self):
        a = twc.Widget(id='a')
        b = twc.Widget(id='b')
        test = twc.widgets.WidgetBunch([a, b])
        assert(len(test) == 2)
        assert([w for w in test] == [a, b])
        assert(test[0] is a)
        assert(test[1] is b)
        assert(test.a is a)
        assert(test.b is b)
        try:
            test.c
            assert(False)
        except AttributeError, e:
            assert(str(e) == "Widget has no child named 'c'")

    def xxtest_wb_nonwidget(self):
        try:
            test = twc.widgets.WidgetBunch(['hello'])
            assert(False)
        except twc.WidgetError, e:
            assert(str(e) == 'WidgetBunch may only contain Widgets')

    def xxtest_wb_dupe(self):
        try:
            test = twc.widgets.WidgetBunch([twc.Widget(id='a'), twc.Widget(id='a')])
            assert(False)
        except twc.WidgetError, e:
            assert(str(e) == "WidgetBunch contains a duplicate id 'a'")

    def test_cw_propagate(self):
        test = twc.CompoundWidget(id='a', template='x', children=[
            twc.Widget.cls(id='b'),
            twc.Widget.cls(id='c'),
        ]).req()
        test.value = {'b':1, 'c':2}
        test.prepare()
        assert(test.children.b.value == 1)
        assert(test.children.c.value == 2)

        class A:
            pass
        a = A()
        a.b = 10
        a.c= 20
        test.value = a
        test.prepare()
        assert(test.children.b.value == 10)
        assert(test.children.c.value == 20)


    #--
    # Repeating Widget Bunch
    #--
    def test_rwb(self):
        test = twc.RepeatingWidget.cls(child=twc.Widget).req()
        testapi.request(1)
        test.value = ['a', 'b', 'c']
        test.prepare()
        for i in range(4):
            assert(test.children[i].repetition == i)
        assert(test.children[0] is not test.children[1])

    def test_rw_propagate(self):
        test = twc.RepeatingWidget.cls(child=twc.Widget).req()
        testapi.request(1)
        test.value = ['a', 'b', 'c']
        test.prepare()
        assert(len(test.children) == 4)
        print [w.value for w in test.children]
        assert([w.value for w in test.children] == ['a', 'b', 'c', None])

    def test_rw_length(self):
        test = twc.RepeatingWidget.cls(child=twc.Widget).req()

        test.value = range(10)
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 11)

        test.extra_reps = 5
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 15)

        test.max_reps = 10
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 10)

        test.max_reps = 30
        test.min_reps = 20
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 20)

    #--
    # Display only
    #--
    def test_display_only(self):
        a = twc.Widget(id='a')
        test = twc.DisplayOnlyWidget(child=a, template='xyz')
        assert(a.parent is None)
        assert(test.child.parent.template == test.template)
        testapi.request(1)
        test = test.req()
        test.value = 10
        test.prepare()
        assert(test.child.value == 10)

