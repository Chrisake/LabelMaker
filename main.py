import fileManager as fm
import re
from consolemenu import *
from consolemenu.items import *
from http.server import HTTPServer
from server import Server
import time

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
  print(f'[{time.asctime()}]\tStart Server - {HOST_NAME}:{PORT}')
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      pass
  httpd.server_close()
  print(f'[{time.asctime()}]\tStop Server - {HOST_NAME}:{PORT}')
  raise NotImplementedError('Web App has not been implemented yet.')

def CheckJSFiles():
  raise NotImplementedError('Has not been implemented yet.')

def SortFileContents():
  raise NotImplementedError('Has not been implemented yet.')

if __name__=="__main__":
  manager = fm.fileManager()
  manager.selectFolder()
  
  menu = ConsoleMenu("Label Maker", "Please Choose an action to continue")
  AddLabelsSubMenu = ConsoleMenu("Add Labels","Choose a method:")
  AddFromConsole = FunctionItem("use Command Line", AddLabelsCommandLine, [])
  AddFromWebApp = FunctionItem("use Web Application", StartWebAppServer, [])
  RepairSubMenu = ConsoleMenu("Repair Files","Choose an action:")
  CheckFiles = FunctionItem("Check Javascript import files", CheckJSFiles, [])
  SortFiles = FunctionItem("Sort file contents", SortFileContents, [])
  AddLabelsSubMenu.append_item(AddFromConsole)
  AddLabelsSubMenu.append_item(AddFromWebApp)
  RepairSubMenu.append_item(CheckFiles)
  RepairSubMenu.append_item(SortFiles)
  al_submenu_item = SubmenuItem("Add Labels", AddLabelsSubMenu, menu)
  r_submenu_item = SubmenuItem("Repair Files", RepairSubMenu, menu)
  menu.append_item(al_submenu_item)
  menu.append_item(r_submenu_item)
  menu.show()