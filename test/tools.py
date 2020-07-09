import datetime
import io
import os
import subprocess
"""
从git获取文件修改时间 执行git命令 git log
"""
def getLastModifiedYear(file):
    print("processing " + file)
    startingDir = os.curdir;
    print(startingDir)
    if file.startswith(startingDir):
        file = file[len(startingDir):]
    if file.startswith("/"):
        file = file[1:]
    startYear = 0;
    endYear = 0;
    print(file)
    proc = subprocess.Popen(["git", "log", "--", file], stdout=subprocess.PIPE)
    print(proc)
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        if not line: break
        l = str(line)
        print(l)
        if l.startswith("Date:"):
            l = l[len("Date:"):].strip()
            dt = datetime.datetime.strptime(l, "%a %b %d %H:%M:%S %Y %z")
            if endYear == 0:
                endYear = dt.year
                startYear = dt.year
            if dt.year > endYear:
                endYear = dt.year
            if dt.year < startYear:
                startYear = dt.year
    if startYear == 0:
        startYear = datetime.datetime.fromtimestamp(os.path.getmtime(file));
        endYear = startYear
    if startYear == endYear:
        return str(startYear)
    else:
        return "%s, %s" %(startYear, endYear)


res = getLastModifiedYear("app.py");
print(res)