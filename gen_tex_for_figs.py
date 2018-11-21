import os
import sys
import argparse

__cur_dir = os.path.dirname(os.path.realpath(__file__))
figs_dir = os.path.join(__cur_dir, 'figures/')

target_dir = os.path.join(__cur_dir, 'targets/')
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

template_fp = os.path.join(__cur_dir, 'fig_template.tmp')

def is_tikz_file(fp):
    fh = open(fp, 'r')
    count = 0
    for l in fh:
        if l.find('tikzpicture') != -1:
            count += 1

    fh.close()
    if count == 2:
        return True
    else:
        return False



def is_axis_file(fp):
    fh = open(fp, 'r')
    if is_tikz_file(fp):
        return False
    count = 0
    for l in fh:
        if l.find('\\begin{axis}') != -1 or l.find('\\end{axis}') != -1:
            count += 1

    fh.close()

    if count == 2:
        return True
    else:
        return False




def get_all_tex_files():
    res = []
    for f in os.listdir(figs_dir):
        if not f.endswith('.tex'):
            continue
        fp = os.path.join(figs_dir, f)
        res.append(fp)

    return res

def extract_tikz_from_file(fp):
    res = ''
    got_begin_tikz = False
    end_tikz = False
    for line in open(fp, 'r'):
        line = line.strip()
        if line.startswith('%'):
            continue

        if line.startswith('\\begin{tikzpicture}'):
            got_begin_tikz = True


        if got_begin_tikz and (not end_tikz):
            res += line + '\n'

        if line.startswith('\\end{tikzpicture}'):
            end_tikz = True

    return res

def extract_axis_from_file(fp):
    res = ''
    got_begin_tikz = False
    end_tikz = False
    for line in open(fp, 'r'):
        line = line.strip()
        if line.startswith('%'):
            continue

        if line.startswith('\\begin{axis}'):
            got_begin_tikz = True


        if got_begin_tikz and (not end_tikz):
            res += line + '\n'

        if line.startswith('\\end{axis}'):
            end_tikz = True

    return res

def extract_content_from_file(fp):
    if is_tikz_file(fp):
        return extract_tikz_from_file(fp)
    if is_axis_file(fp):
        res = '\\begin{tikzpicture}\n'
        res += extract_axis_from_file(fp)
        res += '\n\\end{tikzpicture}\n'
        return res
    else:
        return open(fp, 'r').read()


def gen_standalone_for_tex(fp):
    template_str = open(template_fp, 'r').read()

    target_fp = os.path.join(target_dir, os.path.basename(fp))
    content = extract_content_from_file(fp)
    if content is None:
        return None
    res = template_str.replace('{{TEX_HERE}}', content)
    open(target_fp, 'w').write(res)
    return target_fp



def gen_all_targets():
    targets = []
    fs = get_all_tex_files()
    for f in fs:
        fp = gen_standalone_for_tex(f)
        if fp is None :
            continue
        targets.append(os.path.basename(fp))

    return targets


def  build_pdf_for_target(target):
    print '\n\n************ Generating {}\n\n'.format(target)
    cmd = 'cd targets && xelatex ' + target + ' && cd ..'
    os.system(cmd)

def mv_pdf_files(target):
    cmd = 'cp targets/*.pdf pdfs/'
    os.system(cmd)

def do_for_all_fig_files():
    ts = gen_all_targets()
    for t in ts:
        build_pdf_for_target(t)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate pdf for file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', help='Ask Xuepeng')
    args = parser.parse_args()
    filename = args.file

    if filename == 'all':
        do_for_all_fig_files()
    else:
        fp = os.path.join(figs_dir, filename)
        fp = gen_standalone_for_tex(fp)
        build_pdf_for_target(fp)
        mv_pdf_files(fp)




