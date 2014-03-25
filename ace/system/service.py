from ace.system.utils import *

def control(service_name, action):
  issueCmd(['service', service_name, action])
