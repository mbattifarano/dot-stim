import subprocess as sh
import sys

MATLAB_DUMP='.matlab-dump'

def parse_path(fname):
    path_as_list=fname.split('/')
    path_to_file='/'.join(path_as_list[0:-1])
    filename = path_as_list[-1]
    return path_to_file, filename

def format_input(fn_name,*args):
    if len(args)>0:
        fn_input='\''+'\',\''.join(args)+'\''
        fn_str='%s(%s)'%(fn_name,fn_input)
    else:
        fn_str=fn_name
    err_msg='disp(lasterr)'
    input_str='try;%s;catch;%s;exit(1);end;exit(0);'
    input_str=input_str%(fn_str,err_msg)
    call_matlab='matlab -nojvm -nodisplay -nosplash'
    exec_str='{} -r \"{}\" > {}'.format(call_matlab,input_str,MATLAB_DUMP)
    return exec_str

def first(string):
    if type(string)!=str:
        raise TypeError
    try:
        return string[0]
    except:
        return ''

def matlab(fn_name,*args,**kwargs):
    try:
        verbose=kwargs.get('verbose')
    except KeyError:
        verbose=3
    path_to, fn_name = parse_path(fn_name)
    if first(path_to)!='/':
        path_to='./'+path_to
	cmd=format_input(fn_name,*args)
	exec_str='cd '+path_to+';'+cmd+';'+'cd $OLDPWD;'
	sys.stdout.write(exec_str*(verbose>=2))
    ret_code = sh.check_call(exec_str,shell=True)
    #sys.stdout.write(ret_code*(verbose>=2))

    matlab_out = sh.check_output(['tail','-n','+10',MATLAB_DUMP])
    sys.stdout.write(matlab_out.strip('\n')*(verbose>=3))
    
    sh.check_call(['rm',MATLAB_DUMP])
    return ret_code


if __name__=='__main__':
    matlab(*sys.argv[1:])

