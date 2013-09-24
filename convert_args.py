import re

def dict_to_arg_str(d):
# definitely a super sketch hack -- map return a list of `None' values
# since l.extend is an in-place list operator so l is the variable we want
    l=[]
    d=reformat_dict(d)
    map(l.extend,dict_to_arg_list(d))
    return ' '.join(map(str,l))

def dict_to_arg_list(d):
    d=reformat_dict(d)
    return map(list,d.keys(),d.values())

def dict_to_arg_file(d,path):
    d=reformat_dict(d)
    l=dict_to_arg_list(d)
    l=[ ' '.join(map(str,el)) for el in l]
    s='\n'.join(l)
    with open('{}/args'.format(path)) as f:
        f.write(s)
    return s

# NOTE: reformat_dict(reformat(d))==reformat_dict(d)
def reformat_dict(d): return dict(zip(map(reformat_key,d.keys()),d.values()))

def reformat_key(key): return '--'+key.replace('--','').replace('_','-')
    
    
