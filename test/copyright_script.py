#!/usr/bin/python

# checks copyright statements
"""repo批量添加copyright脚本"""
import os
import os.path
import sys
import re

#===============================================================================
# Global Variables
#===============================================================================
filesNotCheck=["build.xml","component.xml"]
endingsNotCheck=("gif",".zip",".png",".jpg",".jpeg",".jar",".class")
buzzwords=("Kenexa")
copyRightJavaStatementPattern= '/\*.*\*/'
copyRightPropertiesStatementPattern='#'
copyRightJavaScriptStatementPattern= '/\*.*\*/'
copyRightXmlStatementPattern='<!--.*-->'
copyRightJspStatementPattern='<%--.*--%>'
#===============================================================================
# Function
#===============================================================================
def searchForJavaCopyRight(file,tmpFileName,logFile):
  fileToCheck = open(file, encoding='utf-8', errors='ignore', mode="r")
  tmpFile = tmpFile = open(tmpFileName,  encoding='utf-8',mode="w")
  #adding new copyright
  tmpFile.write("/* ****************************************************************** */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* IBM Confidential                                                   */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* OCO Source Materials                                               */\n")
  tmpFile.write("/* 5900-A06                                                           */\n")
  tmpFile.write("/* \u00a9 Copyright IBM Corp. 2017                                         */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* The source code for this program is not published or otherwise     */\n")
  tmpFile.write("/* divested of its trade secrets, irrespective of what has been       */\n")
  tmpFile.write("/* deposited with the U.S. Copyright Office.                          */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* ****************************************************************** */\n")
  
  #assumption: copyright header is always in the beginning
  copyRight = True
  copyRightFound = False
  buzzwordFound = False
  for line in fileToCheck:
    if copyRight:
      copyRightJavaStatement = re.search(copyRightJavaStatementPattern, line)
      if copyRightJavaStatement:
        copyRightFound = True
        copyRight = True
      elif not copyRightFound and line.strip()=="":
        copyRight = True
      elif "package" in line:
        tmpFile.write(line)
      else:
        copyRight = False
    if not copyRight:
      tmpFile.write(line)
      if buzzwords in line:
        if not buzzwordFound:
          logFile.write(file+"\n")
          buzzwordFound = True
        logFile.write("   "+line)
  tmpFile.close()
  fileToCheck.close()
  
def searchForPropertiesCopyRight(file,tmpFileName,logFile):
  fileToCheck = open(file, encoding='utf-8', errors='ignore', mode='r')
  tmpFile = open(tmpFileName, encoding='utf-8',mode="w")
  #adding new copyright
  tmpFile.write("# ****************************************************************** \n")
  tmpFile.write("#                                                                    \n")
  tmpFile.write("# Licensed Materials - Property of IBM Corp.                         \n")
  tmpFile.write("#                                                                    \n")
  tmpFile.write("# 5900-A06                                                           \n")
  tmpFile.write("# \u00a9 Copyright IBM Corp. 2017                                    \n")
  tmpFile.write("#                                                                    \n")
  tmpFile.write("# US Government Users Restricted Rights - Use,                       \n")
  tmpFile.write("# duplication or disclosure restricted by GSA ADP Schedule           \n")
  tmpFile.write("# Contract with IBM Corp.                                            \n")
  tmpFile.write("#                                                                    \n")
  tmpFile.write("# ****************************************************************** \n")
  
  #assumption: copyright header is always in the beginning
  copyRight = True
  copyRightFound = False
  buzzwordFound = False
  for line in fileToCheck:
    if copyRight:
      copyRightPropertiesStatement = re.search(copyRightPropertiesStatementPattern, line)
      if copyRightPropertiesStatement:
        copyRightFound = True
        copyRight = True
      elif not copyRightFound and line.strip()=="":
        copyRight = True
      else:
        copyRight = False
    if not copyRight:
      tmpFile.write(line)
      if buzzwords in line:
        if not buzzwordFound:
          logFile.write(file+"\n")
          buzzwordFound = True
        logFile.write("   "+line)
  tmpFile.close()
  fileToCheck.close()

def searchForJavaScriptCssCopyRight(file,tmpFileName,logFile):
  fileToCheck = open(file, encoding='utf-8', errors='ignore', mode='r')
  tmpFile = open(tmpFileName, encoding='utf-8',mode="w")
  #adding new copyright
  tmpFile.write("/* ****************************************************************** */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* Licensed Materials - Property of IBM Corp.                         */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* 5900-A06                                                           */\n")
  tmpFile.write("/* \u00a9 Copyright IBM Corp. 2017                                         */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* US Government Users Restricted Rights - Use,                       */\n")
  tmpFile.write("/* duplication or disclosure restricted by GSA ADP Schedule           */\n")
  tmpFile.write("/* Contract with IBM Corp.                                            */\n")
  tmpFile.write("/*                                                                    */\n")
  tmpFile.write("/* ****************************************************************** */\n")
  copyRight = True
  copyRightFound = False
  buzzwordFound = False
  for line in fileToCheck:
    if copyRight:
      copyRightJavaScriptStatement = re.search(copyRightJavaScriptStatementPattern, line)
      if copyRightJavaScriptStatement:
        copyRightFound = True
        copyRight = True
      elif not copyRightFound and line.strip()=="":
        copyRight = True
      else:
        copyRight = False
    if not copyRight:
      tmpFile.write(line)
      if buzzwords in line:
        if not buzzwordFound:
          logFile.write(file+"\n")
          buzzwordFound = True
        logFile.write("   "+line)
  tmpFile.close()
  fileToCheck.close()

def searchForXmlCopyRight(file,tmpFileName,logFile):
  fileToCheck = open(file, encoding='utf-8', errors='ignore', mode='r')
  tmpFile = open(tmpFileName, encoding='utf-8',mode="w")
  #adding new copyright
  tmpFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
  tmpFile.write("<!-- ****************************************************************** -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- Licensed Materials - Property of IBM Corp.                         -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- 5900-A06                                                           -->\n")
  tmpFile.write("<!-- \u00a9 Copyright IBM Corp. 2017                                         -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- US Government Users Restricted Rights - Use,                       -->\n")
  tmpFile.write("<!-- duplication or disclosure restricted by GSA ADP Schedule           -->\n")
  tmpFile.write("<!-- Contract with IBM Corp.                                            -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- ****************************************************************** -->\n")
  
  #assumption: copyright header is always in the beginning
  copyRight = True
  copyRightFound = False
  buzzwordFound = False
  for line in fileToCheck:
    if copyRight:
      copyRightXmlStatement = re.search(copyRightXmlStatementPattern, line)
      if copyRightXmlStatement:
        copyRightFound = True
        copyRight = True
      elif not copyRightFound and line.strip()=="":
        copyRight = True
      elif "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" in line:
        additionalInput= line[line.index(">")+1:].strip()
        if additionalInput != "":
          tmpFile.write(additionalInput)
      else:
        copyRight = False
    if not copyRight:
      tmpFile.write(line)
      if buzzwords in line:
        if not buzzwordFound:
          logFile.write(file+"\n")
          buzzwordFound = True
        logFile.write("   "+line)
  tmpFile.close()
  fileToCheck.close()

def searchForJspCopyRight(file,tmpFileName,logFile):
  fileToCheck = open(file, encoding='utf-8', errors='ignore', mode='r')
  tmpFile = open(tmpFileName, encoding='utf-8',mode="w")
  #adding new copyright
  tmpFile.write("<%-- ****************************************************************** --%>\n")
  tmpFile.write("<%--                                                                    --%>\n")
  tmpFile.write("<%-- Licensed Materials - Property of IBM Corp.                         --%>\n")
  tmpFile.write("<%--                                                                    --%>\n")
  tmpFile.write("<%-- 5900-A06                                                           --%>\n")
  tmpFile.write("<%-- \u00a9 Copyright IBM Corp. 2017                                         --%>\n")
  tmpFile.write("<%--                                                                    --%>\n")
  tmpFile.write("<%-- US Government Users Restricted Rights - Use,                       --%>\n")
  tmpFile.write("<%-- duplication or disclosure restricted by GSA ADP Schedule           --%>\n")
  tmpFile.write("<%-- Contract with IBM Corp.                                            --%>\n")
  tmpFile.write("<%--                                                                    --%>\n")
  tmpFile.write("<%-- ****************************************************************** --%>\n")
  copyRight = True
  copyRightFound = False
  buzzwordFound = False
  for line in fileToCheck:
    if copyRight:
      copyRightJspStatement = re.search(copyRightJspStatementPattern, line)
      if copyRightJspStatement:
        copyRightFound = True
        copyRight = True
      elif not copyRightFound and line.strip()=="":
        copyRight = True
      elif re.search("<%@.*%>",line):
        tmpFile.write(line)
      else:
        copyRight = False
    if not copyRight:
      tmpFile.write(line)
      if buzzwords in line:
        if not buzzwordFound:
          logFile.write(file+"\n")
          buzzwordFound = True
        logFile.write("   "+line)
  tmpFile.close()
  fileToCheck.close()


def searchForHtmlCopyRight(file,tmpFileName,logFile):
  fileToCheck = open(file, encoding='utf-8', errors='ignore', mode='r')
  tmpFile = open(tmpFileName, encoding='utf-8',mode="w")
  #adding new copyright
  tmpFile.write("<!-- ****************************************************************** -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- Licensed Materials - Property of IBM Corp.                         -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- 5900-A06                                                           -->\n")
  tmpFile.write("<!-- \u00a9 Copyright IBM Corp. 2017                                         -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- US Government Users Restricted Rights - Use,                       -->\n")
  tmpFile.write("<!-- duplication or disclosure restricted by GSA ADP Schedule           -->\n")
  tmpFile.write("<!-- Contract with IBM Corp.                                            -->\n")
  tmpFile.write("<!--                                                                    -->\n")
  tmpFile.write("<!-- ****************************************************************** -->\n")
  
  #assumption: copyright header is always in the beginning
  copyRight = True
  copyRightFound = False
  buzzwordFound = False
  for line in fileToCheck:
    if copyRight:
      copyRightXmlStatement = re.search(copyRightXmlStatementPattern, line)
      if copyRightXmlStatement:
        copyRightFound = True
        copyRight = True
      elif not copyRightFound and line.strip()=="":
        copyRight = True
      else:
        copyRight = False
    if not copyRight:
      tmpFile.write(line)
      if buzzwords in line:
        if not buzzwordFound:
          logFile.write(file+"\n")
          buzzwordFound = True
        logFile.write("   "+line)
  tmpFile.close()
  fileToCheck.close()

#===============================================================================
# Main
#===============================================================================
if len(sys.argv) < 3:
  print ("Syntax:")
  print ("copyright.py <starting-dir> <temp-dir>")
else:
  startingDir = sys.argv[1]
  tempDir = sys.argv[2]
  
  if os.path.exists(startingDir):
    #create log file for buzzwords
    if not os.path.exists(tempDir):
      os.makedirs(tempDir)
    buzzwordFile = open(os.path.join(tempDir,"buzzword.log"), encoding='utf-8', errors='ignore', mode='w')
    missingFile = open(os.path.join(tempDir,"missing.log"), encoding='utf-8', errors='ignore', mode='w')
    for (path, dirs, files) in os.walk(startingDir):
      for name in files:
        if name not in filesNotCheck:
          destDirName=str(path).replace(startingDir,tempDir)
          if not os.path.exists(destDirName):
            os.makedirs(destDirName)
          if name.endswith(".java"):
            searchForJavaCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          elif name.endswith(".properties"):
            searchForPropertiesCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          elif name.endswith(".js"):
            searchForJavaScriptCssCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          elif name.endswith(".xml"):
            searchForXmlCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          elif name.endswith(".jsp"):
            searchForJspCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          elif name.endswith(".html") or name.endswith(".htm"):
            searchForHtmlCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          elif name.endswith(".css") or name.endswith(".less"):
            searchForJavaScriptCssCopyRight(os.path.join(path,name),os.path.join(destDirName,name),buzzwordFile)
          else:
            if not name.endswith(endingsNotCheck):
              missingFile.write(str(os.path.join(path,name))+"\n")
    buzzwordFile.close()
    missingFile.close()
  else:
    print ("Error: Directory: "+startingDir+" does not exist.")
