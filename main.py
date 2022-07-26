import fileManager as fm
import re
from consolemenu import *
from consolemenu.items import *
from http.server import HTTPServer
from server import Server
import time
import json
import os
from tabulate import tabulate as tb
import math
from tqdm import tqdm

HOST_NAME = 'localhost'
PORT = 8000

def safeInput(text, reg='.*'):
  result = None
  while result is None or re.search(reg, result) is None:
    if result is not None: print('Invalid Input')
    result = input(text)
  return result

def AddLabelsCommandLine():
  oldCat = 'Misc'
  while(True):
    print('Input New Label:\n'+'='*30)
    fn = safeInput('Api Name: ', '^[a-zA-Z]+$')
    val = safeInput('Value: ', '.+')
    desc = safeInput('Description: ', '.+')
    cat = input(f'Category{"" if oldCat is None else f"(default: {oldCat})"}: ')
    if cat == '': cat = oldCat
    lang = input('Language(default: en_US): ')
    manager.addLabel(fm.Label(fn,val,desc,cat,lang))
    oldCat = cat
    print('='*30+'\n')

def StartWebAppServer():
  httpd = HTTPServer((HOST_NAME,PORT),Server)
  httpd.RequestHandlerClass.manager = manager
  print(f'[{time.asctime()}]\tStart Server - {HOST_NAME.lower() if "http" in HOST_NAME.lower() else f"http://{HOST_NAME.lower()}"}:{PORT}')
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      pass
  httpd.server_close()
  print(f'[{time.asctime()}]\tStop Server - {HOST_NAME}:{PORT}')

def CheckFileConsistency():
  labels = manager.getLabelsFromJS('AK')
  labels = labels + manager.getLabelsFromJS('LZ')
  inconsistent = [l for l in labels if l['name']!=l['object']]
  if len(inconsistent) == 0:
    print('No inconsistent labels found in JS files')
  else:
    print('Labels with different names from customLabel:')
    for l in inconsistent:
      print(f'{l["name"]} - {l["object"]}')
  input('Press Enter to continue...')

def SortFileContents():
  labelsObjs = manager.getLabelsFromXML()
  JSlabelsAK = manager.getLabelsFromJS(file='AK')
  JSlabelsLZ = manager.getLabelsFromJS(file='LZ')
  labelsObjs.sort(key= lambda x: x['fullName'].lower())
  manager.saveLabelsToXML(labelsObjs)
  JSlabelsAK.sort(key=lambda x: x['name'].lower())
  manager.saveLabelsToJS(JSlabelsAK,file='AK')
  JSlabelsLZ.sort(key=lambda x: x['name'].lower())
  manager.saveLabelsToJS(JSlabelsLZ,file='LZ')
  print('DONE!')
  input('Press Enter to continue...')

def CheckJSFiles():
  labelsObjs = manager.getLabelsFromXML()
  JSlabelsAK = manager.getLabelsFromJS(file='AK')
  JSlabelsLZ = manager.getLabelsFromJS(file='LZ')
  labelApis =  set()
  for l in JSlabelsAK:
    labelApis.add(l['object'])
  for l in JSlabelsLZ:
    labelApis.add(l['object'])
  notImportedLabels = []
  for l in labelsObjs:
    if not l['fullName'] in labelApis:
      notImportedLabels.append(l['fullName'])
  if len(notImportedLabels) > 0:
    print(f'The Following label Api names are not imported in JS files: {len(notImportedLabels)}')
    printSplitStrings(notImportedLabels,5)
    input('Press Enter to continue...')
    menu = ConsoleMenu(f"What do you want to do with those {len(notImportedLabels)} labels?", "")
    def delete():
      nil = set(notImportedLabels)
      newObjs = []
      for obj in labelsObjs:
        if obj['fullName'] not in nil:
          newObjs.append(obj)
      manager.saveLabelsToXML(newObjs)
    def imprt():
      for l in notImportedLabels:
        if l[0].lower()<='k':
          JSlabelsAK.append({'name':l,'object':l})
        else:
          JSlabelsLZ.append({'name':l,'object':l})
      JSlabelsAK.sort(key=lambda x: x['name'].lower())
      manager.saveLabelsToJS(JSlabelsAK,file='AK')
      JSlabelsLZ.sort(key=lambda x: x['name'].lower())
      manager.saveLabelsToJS(JSlabelsLZ,file='LZ')
    menu.append_item(FunctionItem("Delete labels from CustomLabels file",delete,[],should_exit=True))
    menu.append_item(FunctionItem("Import labels to JS",imprt,[],should_exit=True))
    menu.show()
  else:
    print('All Labels are imported')
  input('Press Enter to continue...')

def stringConstantLength(s,length):
  return "{:<{length}}".format(s,length=length) if len(s)<length else s[:length-3]+'...'

def LookForUnusedLabels():
  labels = manager.getLabelsFromXML()
  rootdir = manager.rootFolder
  uses = {}
  for l in labels:
    uses[l['fullName']] = 0
  apiNames = list(uses.keys())
  t = tqdm(list(os.walk(rootdir+'\\src')))
  for folder,dirs,file in t:
    if len([folder for exc in ['contentassets','documents','siteDotComSites','staticresources','translations'] if exc in folder])>0: continue
    for files in [f for f in file if f not in ['labelsAK.js','labelsLZ.js','CustomLabels.labels']]:
      t.desc = stringConstantLength(files,40)
      try:
        with open(os.path.join(folder,files),'r',encoding='UTF-8') as fileObj:
          fileData = fileObj.read()
        for l in apiNames:
          if l in fileData:
            uses[l] += 1
      except:
        print(folder)
  
  unusedLabels = [l for l in apiNames if uses[l]==0]
  if len(unusedLabels) > 0:
    print(f'{len(unusedLabels)} Unused Labels:')
    printSplitStrings(unusedLabels,5)
    
  else:
    print('No unused labels found')
  input('Press Enter to continue...')

def printSplitStrings(ls,columns=3):
  num = len(ls)
  itemsPerColumn = math.ceil(num/columns)
  table = []
  for i in range(itemsPerColumn):
    row=[]
    for c in range(columns):
      idx = c * itemsPerColumn + i
      row.append(ls[idx] if idx < num else '')
    table.append(row)
  print(tb(table))
  

def loadConfiguration():
  try:
    with open('project.config','r') as configFile:
      data = configFile.read()
    config = json.loads(data)
    return config
  except Exception as e:
    pass
  return { 'rootDirectory': None }

def saveConfiguration(config):
  with open('project.config','w') as configFile:
    data = configFile.write(json.dumps(config))

if __name__=="__main__":
  config = loadConfiguration()
  manager = fm.fileManager()
  if manager.selectFolder(config['rootDirectory']) is None:
    exit()
  config['rootDirectory'] = manager.rootFolder
  saveConfiguration(config)

  menu = ConsoleMenu("Label Maker", "Please Choose an action to continue")
  AddLabelsSubMenu = ConsoleMenu("Add Labels","Choose a method:")
  RepairSubMenu = ConsoleMenu("Repair Files","Choose an action:")
  AddLabelsSubMenu.append_item(FunctionItem("Command Line", AddLabelsCommandLine, []))
  AddLabelsSubMenu.append_item(FunctionItem("Web Application", StartWebAppServer, []))
  RepairSubMenu.append_item(FunctionItem("Check Javascript import files", CheckJSFiles, []))
  RepairSubMenu.append_item(FunctionItem("Reformat label files", SortFileContents, []))
  RepairSubMenu.append_item(FunctionItem("Check File Consistency", CheckFileConsistency, []))
  RepairSubMenu.append_item(FunctionItem("Look for unused labels", LookForUnusedLabels, []))
  al_submenu_item = SubmenuItem("Add Labels", AddLabelsSubMenu, menu)
  r_submenu_item = SubmenuItem("Repair Files", RepairSubMenu, menu)
  menu.append_item(FunctionItem("Change Project Directory", manager.selectFolder, []))
  menu.append_item(al_submenu_item)
  menu.append_item(r_submenu_item)
  menu.show()