import os, re

def rename(foldername):
    folder = foldername
    file_list = sorted(os.listdir(folder))
    for f in file_list:
        if f.endswith('\r'):
            old_path = folder + '/' + f
            stripped_f = re.sub(r'\r', '', f)
            new_path = folder + '/' + stripped_f
            os.rename(old_path, new_path)
    return

rename('source_before')
rename('source_after')