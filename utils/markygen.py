#! python3
"""
This is a terrible script that generates markdown from doxygen output.
"""

import argparse
from pprint import pprint
from lxml import etree as et
from mako.template import Template


class DoxyObject(object):
    def __init__(self, xml):
        self._xml = xml
        self.brief = self._get('briefdescription/para')
        self.desc = self._get('detaileddescription/para')

    def _get(self, xpath):
        try:
            return self._xml.xpath(xpath)[0].text
        except:
            return ''


class Parameter(DoxyObject):
    def __init__(self, xml):
        super().__init__(xml)
        self.name = self._get('parameternamelist/parametername')
        self.desc = self._get('parameterdescription/para')


class Function(DoxyObject):
    def __init__(self, xml):
        super().__init__(xml)
        self.visibility = xml.get('prot')
        self.is_static = xml.get('static') == 'yes'
        self.is_const = xml.get('const') == 'yes'
        self.is_explicit = xml.get('explicit') == 'yes'
        self.is_inline = xml.get('inline') == 'yes'
        self.is_virtual = xml.get('virtual') == 'virtual'
        self.name = self._get('name')
        self.type = self._get('type')
        self.argsstr = self._get('argsstring')
        try:
            self.params = [Parameter(p) for p in xml.xpath('detaileddescription/para/parameterlist[@kind="param"]')[0]]
        except IndexError:
            self.params = []
        try:
            self.tparams = [Parameter(p)
                            for p in xml.xpath('detaileddescription/para/parameterlist[@kind="templateparam"]')[0]]
        except IndexError:
            self.tparams = []

        self.note = self._get('detaileddescription/para/simplesect[@kind="note"]/para')
        self.returns = self._get('detaileddescription/para/simplesect[@kind="return"]/para')


class Class(DoxyObject):
    def __init__(self, xml):
        super().__init__(xml)
        self.name = self._get('compoundname')
        self.includes = self._get('includes')
        self.functions = [Function(f)
                          for f in xml.xpath('sectiondef[@kind="public-func"]/memberdef[@kind="function"]')]
        for f in self.functions:
            pprint(f.__dict__)

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('template')
parser.add_argument('output')
args = parser.parse_args()

tree = et.parse(args.input)
classes = [Class(i) for i in tree.xpath('//compounddef[@kind="class"]')]

with open(args.template) as t:
    tdata = t.read()
    mytemplate = Template(tdata)
    with open(args.output, 'w') as f:
        f.write(mytemplate.render(classes=classes))
