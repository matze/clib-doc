import os
import subprocess
import string
import tempfile
import shutil
import xml.etree.ElementTree as et
import jinja2
from operator import attrgetter
from pkg_resources import resource_string


class Type(object):
    def __init__(self, node):
        self.refid = None

        if node.text:
            self.name = node.text
        else:
            try:
                self.name = node[0].text
            except IndexError:
                pass

            refs = node.findall('ref')

            if refs:
                self.refid = refs[0].get('refid')

    def __str__(self):
        return self.name


class Parameter(object):
    def __init__(self, param):
        declname = param.findall('declname')
        self.name = declname[0].text if declname else ''
        self.type = Type(param.findall('type')[0])

    def __str__(self):
        return "{} {}".format(self.type, self.name)


class Struct(object):
    def __init__(self, name, refid, structroot):
        self.name = name
        self.refid = refid
        self.detailed = [p.text for p in structroot.findall(".//detaileddescription/para")]


class Function(object):
    def __init__(self, name, refid, memberdef):
        def get_text(name):
            return memberdef.findall(name)[0].text

        self.name = name
        self.refid = refid
        self.definition = get_text('definition')
        self.args = get_text('argsstring')
        self.params = [Parameter(p) for p in memberdef.findall('param')]
        self.brief = get_text('briefdescription')
        self.detailed = [p.text for p in memberdef.findall("./detaileddescription/para")]
        self.type = Type(memberdef.findall('type')[0])


def rpad(value, num):
    fmt = '{:>' + str(num) + '}'
    return fmt.format(value)


def lpad(value, num):
    fmt = '{:<' + str(num) + '}'
    return fmt.format(value)


def param_list(params):
    for p in params:
        if p.type.refid:
            yield '<a href="#{}">{}</a> {}'.format(p.type.refid, p.type.name, p.name)
        else:
            yield '{} {}'.format(p.type, p.name)


class Generator(object):
    def __init__(self, pkg, pkg_path, dest_path='.'):
        self.pkg = pkg
        self.pkg_path = pkg_path
        self.dest_path = dest_path
        self._tmpdir = None

    def run(self):
        sources = [os.path.join(self.pkg_path, s) for s in self.pkg['src']]

        pid = os.getpid()
        template = string.Template(resource_string('clibdoc', 'data/Doxyfile.in'))
        self._tmpdir = tempfile.mkdtemp()

        subs = dict(project_name=self.pkg['name'],
                    version=self.pkg['version'],
                    input=' '.join(sources),
                    output_directory=self._tmpdir)

        doxyfile = os.path.join(self._tmpdir, 'Doxyfile'.format(pid))

        with open(doxyfile, 'w') as f:
            f.write(template.substitute(subs))

        cmd = ['doxygen', doxyfile]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        if proc.returncode:
            raise Exception(out + err)

        self.generate()

    def generate(self):
        tree = et.parse(os.path.join(self.xml_path, 'index.xml'))
        root = tree.getroot()

        structs = []
        functions = {}

        def refid_root(node):
            fname = os.path.join(self.xml_path, '{}.xml'.format(node.get('refid')))
            return et.parse(fname).getroot()

        for struct in root.findall("./compound[@kind='struct']"):
            name = struct.findall('name')[0].text
            refid = struct.get('refid')
            sroot = refid_root(struct)
            structs.append(Struct(name, refid, sroot))

        files = (x for x in root.findall("./compound[@kind='file']"))

        for f in files:
            froot = refid_root(f)
            funcs = (x for x in f.findall("./member[@kind='function']"))

            for func in funcs:
                name = func[0].text
                refid = func.get('refid')
                query = "./compounddef/sectiondef/memberdef[@id='{}']".format(refid)

                functions[name] = Function(name, refid, froot.findall(query)[0])

        env = jinja2.Environment(loader=jinja2.PackageLoader('clibdoc', 'data'))
        env.filters['lpad'] = lpad
        env.filters['rpad'] = rpad
        env.filters['param_list'] = param_list

        functions = sorted(functions.values(), key=attrgetter('name'))
        template = env.get_template('index.html')

        if not os.path.exists(self.dest_path):
            os.makedirs(self.dest_path)

        with open(os.path.join(self.dest_path, 'index.html'), 'w') as f:
            f.write(template.render(pkg=self.pkg,
                                    functions=functions,
                                    structs=structs))

        with open(os.path.join(self.dest_path, 'clibdoc.css'), 'w') as f:
            f.write(resource_string('clibdoc', 'data/clibdoc.css'))

    def cleanup(self):
        if self._tmpdir:
            shutil.rmtree(self._tmpdir)

    @property
    def xml_path(self):
        return os.path.join(self._tmpdir, 'xml')


def exists():
    binary = 'doxygen'
    return any([os.path.exists(os.path.join(p, binary))
               for p in os.environ["PATH"].split(os.pathsep)])
