import fileManager as fm
import re
from consolemenu import *
from consolemenu.items import *
from http.server import HTTPServer
from server import Server
import time
import json

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
  raise NotImplementedError('Web App has not been implemented yet.')

def CheckJSFiles():
  labels = manager.getLabelsFromJS('AK')
  labels = labels + manager.getLabelsFromJS('LZ')
  inconsistent = [l for l in labels if l['name']!=l['object']]
  if len(inconsistent) == 0:
    print('No inconsistent labels found in JS files')
  else:
    print('Labels with different names from customLabel:')
    for l in inconsistent:
      print(f'{l["name"]} - {l["object"]}')

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

def CheckFileConsistency():
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
    print('The Following label Api names are not imported in JS files:')
    for l in notImportedLabels:
      print(l)
    menu = ConsoleMenu(f"Do you want to delete those {len(notImportedLabels)} labels", "")
    def delete():
      nil = set(notImportedLabels)
      newObjs = []
      for obj in labelsObjs:
        if obj['fullName'] not in nil:
          newObjs.append(obj)
      manager.saveLabelsToXML(newObjs)
    menu.append_item(FunctionItem("Yes",delete,[],should_exit=True))
    menu.show()
  else:
    print('All Labels are imported')

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
  ChangeProjectDir = FunctionItem("Change Project Directory", manager.selectFolder, [])
  AddFromConsole = FunctionItem("Command Line", AddLabelsCommandLine, [])
  AddFromWebApp = FunctionItem("Web Application", StartWebAppServer, [])
  RepairSubMenu = ConsoleMenu("Repair Files","Choose an action:")
  CheckFiles = FunctionItem("Check Javascript import files", CheckJSFiles, [])
  CheckLabelConsistency = FunctionItem("Check File Consistency", CheckFileConsistency, [])
  SortFiles = FunctionItem("Sort file contents", SortFileContents, [])
  AddLabelsSubMenu.append_item(AddFromConsole)
  AddLabelsSubMenu.append_item(AddFromWebApp)
  RepairSubMenu.append_item(CheckFiles)
  RepairSubMenu.append_item(SortFiles)
  RepairSubMenu.append_item(CheckLabelConsistency)
  al_submenu_item = SubmenuItem("Add Labels", AddLabelsSubMenu, menu)
  r_submenu_item = SubmenuItem("Repair Files", RepairSubMenu, menu)
  menu.append_item(ChangeProjectDir)
  menu.append_item(al_submenu_item)
  menu.append_item(r_submenu_item)
  menu.show()