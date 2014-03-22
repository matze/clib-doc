import jinja2


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


def get_env():
    env = jinja2.Environment(loader=jinja2.PackageLoader('clibdoc', 'data'))
    env.filters['lpad'] = lpad
    env.filters['rpad'] = rpad
    env.filters['param_list'] = param_list
    return env
