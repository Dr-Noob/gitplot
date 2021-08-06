#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import sys
import subprocess
import re
import os

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def loc_count(dir, extension):
    len=0
    
    # r=root, d=directories, f = files
    for r, d, f in os.walk(dir):
        for file in f:
            if file.endswith(extension):
                file_path = os.path.join(r, file)
                len += file_len(file_path)
                
    return len            

##############################
# 0. Basic checks

proc = subprocess.Popen(["git --version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
proc.communicate()

if (proc.returncode != 0):
    print('ERROR: git is not installed')
    sys.exit(1)

if(len(sys.argv) != 2):
    print("Usage: " + sys.argv[0] + " GIT_URL")
    sys.exit(1)
    
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

url=sys.argv[1]
if(re.match(regex, url) is None):
    print('ERROR: ' + url + ' is not a valid URL')
    sys.exit(1)
    
##############################
# 1. Download repo    
dir=os.path.basename(url)  

if(os.path.exists(dir)):
    print('WARNING: Directory ' + dir + ' already exists. Skipping git clone')
else:    
  proc = subprocess.Popen(["/usr/bin/git", "clone", url], stdout=subprocess.PIPE)
  proc.communicate()

  if (proc.returncode != 0):
      print('ERROR: git clone failed')
      sys.exit(1)

os.chdir(dir)
proc = subprocess.Popen(["/usr/bin/git", "rev-list", "--remotes"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
(commits, err) = proc.communicate()    

##############################
# 2. Count lines
loc_c=np.array([])
loc_h=np.array([])
loc_makefile=np.array([])
loc_md=np.array([])

for c in commits.splitlines():     
    proc = subprocess.Popen(["/usr/bin/git", "checkout", c], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()        
    
    loc_c = np.append(loc_c, loc_count(".", ".c"))
    loc_h = np.append(loc_h, loc_count(".", ".h"))
    loc_makefile = np.append(loc_makefile, loc_count(".", "Makefile"))
    loc_md = np.append(loc_md, loc_count(".", ".md"))
    
##############################
# 3. ???
loc_c = np.flip(loc_c)
loc_h = np.flip(loc_h)
loc_makefile = np.flip(loc_makefile)
loc_md = np.flip(loc_md)

x = np.arange(0, np.size(loc_c))
    
plt.plot(x, loc_c, label=".c")
plt.plot(x, loc_h, label=".h")
plt.plot(x, loc_makefile, label="Makefile")
plt.plot(x, loc_md, label="Markdown")
plt.plot()

plt.xlabel("Commit number")
plt.ylabel("Lines of Code")
plt.title(dir + ' repository')
plt.legend()
plt.show()    

    
    