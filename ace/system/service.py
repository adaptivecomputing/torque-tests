from ace.system.utils import *

def control(service_name, action):
  issue_cmd(['service', service_name, action])
