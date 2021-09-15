import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/RobotClassification")
from Configuration.Configuration import config
config.config = config
print("config.chunk_size = %s" % config.config.chunk_size)