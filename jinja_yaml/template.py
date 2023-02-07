from jinja2 import Environment, FileSystemLoader
import yaml

config = yaml.full_load(open('test_duts.yaml'))
env = Environment(loader=FileSystemLoader('./templates'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('cisco_template_yaml.j2')

print(template.render(config))
