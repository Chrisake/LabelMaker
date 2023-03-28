import os.path as path
from tkinter import *
from tkinter import filedialog
from bs4 import BeautifulSoup as bs
import re

class fileManager:
  rootFolder = None
  customLabelsPath = None
  labelsAKPath = None
  labelsLZPath = None
  
  def __init__(self) -> None:
    pass
    
  def selectFolder(self,p=None):
    while(True):
      if p is None:
        rootFolder = filedialog.askdirectory(title="Select Project Root Folder")
        if rootFolder == '': return None
      else:
        rootFolder = p
      # Check if folder matches criteria
      customLabelsPath = path.join(rootFolder, rootFolder, 'src/labels/CustomLabels.labels')
      labelsAKPath = path.join(rootFolder, 'src/lwc/labelsAK/labelsAK.js')
      labelsLZPath = path.join(rootFolder, 'src/lwc/labelsLZ/labelsLZ.js')
      p = None
      if not path.exists(customLabelsPath):
        print(f'Could not find Custom labels file:\n{customLabelsPath}')
        input('Press Enter to continue...')
        continue
      if not path.exists(labelsAKPath): 
        print(f'Could not find labelsAK js file:\n{labelsAKPath}')
        input('Press Enter to continue...')
        continue
      if not path.exists(labelsLZPath):
        print(f'Could not find labelsLZ js file:\n{labelsLZPath}')
        input('Press Enter to continue...')
        continue
      print(rootFolder)
      print(customLabelsPath)
      print(labelsAKPath)
      print(labelsLZPath)
      self.rootFolder = rootFolder
      self.customLabelsPath = customLabelsPath
      self.labelsAKPath = labelsAKPath
      self.labelsLZPath = labelsLZPath
      return self.rootFolder
    
  
  def addLabel(self,label):
    labelsObjs = self.getLabelsFromXML()
    
    file = 'AK' if label['fullName'][0].lower()<='k' else 'LZ'
    JSlabels = self.getLabelsFromJS(file=file)
    
    if len([l for l in labelsObjs if l['fullName']==label['fullName']])>0:
      raise ValueError('Api Name already exists')
    if len([l for l in JSlabels if l['name']==label['fullName']])>0:
      raise ValueError('Api Name already exists')
    
    labelsObjs.append(label)
    labelsObjs.sort(key= lambda x: x['fullName'].lower())
    self.saveLabelsToXML(labelsObjs)
    
    JSlabels.append({'name': label['fullName'], 'object': label['fullName']})
    JSlabels.sort(key=lambda x: x['name'].lower())
    self.saveLabelsToJS(JSlabels,file=file)
  
  def getLabelsFromXML(self):
    with open(self.customLabelsPath, 'r', encoding='UTF-8') as fcl:
      data = fcl.read()
    
    xml_data = bs(data,'xml')
    labelsObjs = []
    labels = xml_data.find_all('labels')
    for label in labels:
      newObj = {}
      for content in label.contents:
        if content.name is None or content.name == 'null' or content.name =='': continue
        title = content.name
        value = content.text
        newObj[title] = value
      labelsObjs.append(newObj)
    return labelsObjs
  
  def saveLabelsToXML(self,labels):
    propertOrder = ['fullName','categories','language','protected','shortDescription','value']
    with open(self.customLabelsPath, 'w', encoding='UTF-8') as fcl:
      fcl.write('<?xml version="1.0" encoding="UTF-8"?>\n<CustomLabels xmlns="http://soap.sforce.com/2006/04/metadata">\n')
      for label in labels:
        fcl.write(f'    <labels>\n')
        for p in propertOrder:
          if p in label and label[p] != '' and label[p] != None:
            fcl.write(f'        <{p}>{self.escapeChars(label[p])}</{p}>\n')      
        fcl.write(f'    </labels>\n')
      fcl.write('</CustomLabels>\n')
  
  def escapeChars(self, txt):
    return txt.replace("&","&amp;")\
      .replace("<","&lt;")\
      .replace(">","&gt;")\
      .replace("'","&apos;")\
      .replace("\"","&quot;")\
      .replace("\n","&#xA;")\
      .replace("\\n","&#xA;")\
      .replace("\r","&#xD;")
  
  def getLabelsFromJS(self,file='AK'):
    with  open(self.labelsLZPath if file == 'LZ' else self.labelsAKPath, 'r', encoding='UTF-8') as fl:
      lines = fl.readlines()
    labels = []
    for l in lines:
      if 'import' not in l: break
      name = re.search('(?<=import )\w*(?= from)', l).group()
      obj = re.search("(?<='@salesforce\/label\/c.).*(?=')", l).group()
      labels.append({'name': name, 'object': obj})
    return labels
  
  def saveLabelsToJS(self,labels,file='AK'):
    with  open(self.labelsLZPath if file == 'LZ' else self.labelsAKPath, 'w', encoding='UTF-8') as fl:
      for l in labels:
        fl.write(f"import {l['name']} from '@salesforce/label/c.{l['object']}'\n")
      fl.write('\nexport default {\n')
      for l in labels[:-1]:
        fl.write(f"  {l['name']},\n")
      fl.write(f"  {labels[-1]['name']}\n}}")
    
    
    
  
def Label(name, value, description='' , category='', language='en_US'):
  return {
    'fullName': name,
    'categories': category,
    'language': language if language != '' and language is not None else 'en_US',
    'protected': 'false',
    'shortDescription': description,
    'value': value
  }
  
def Label(obj):
  return {
    'fullName': obj['fullName'],
    'categories': obj['categories'],
    'language': obj['language'] if 'language' in obj and obj['language'] != '' else 'en_US',
    'protected': 'false',
    'shortDescription': obj['shortDescription'],
    'value': obj['value']
  }