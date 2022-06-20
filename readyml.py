import yaml

with open('./../detail.yml','r') as yml:
    config = yaml.safe_load(yml)


print( config['condition']['Nnumber'] )
print( config['condition']['date']['start'] )
print( config['condition']['date']['end'] )
print( config['condition']['rotation_speed'] )
print( config['condition']['feedrate'] )
print( config['condition']['ae'] )
print( config['condition']['ap'] )
print( config['condition']['machining_time'] )
print( config['condition']['process_type'] )