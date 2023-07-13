#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 13:06:56 2022
@requirements: LibreOffice, unoconv, qpdf, Python 3.x + modules (see below)
@author: philip
@version: v0.1, January 2022
"""

# import modules
import os, sys, configparser
import macpassencrypt
from os.path import exists
from imap_tools import MailBox, AND, OR
from binaryornot.check import is_binary

#============================== SUPPORT FUNCTIONS ============================#

def pdf_orientation(myfile):
        
    out  = os.popen('pdfinfo "' + myfile + '"').readlines()
    out2 = ''
    
    for ii in out: 
        if 'Page size' in ii: out2 = ii
        
    out2 = out2.split(' ')
    
    try: cc = out2.index('x') # position of 'x'
    except ValueError:
        return 'NA'
    
    width  = float(out2[cc-1])
    height = float(out2[cc+1])

    if width > height:
        return 'landscape'
    else:
        return 'portrait'
    
def lenfill(instr, length):
    return instr + ' '*(length-len(instr))

#=============================================================================#

# get script path
pypath   = os.path.dirname(os.path.abspath(__file__))

# get script arguments (config file and '-noaction' instruction)
myconfigfile = 'default.cfg'  # no config file as argument, use default.cfg
#myconfigfile = 'config/philconfig.cfg'
flg_action   = True

if len(sys.argv) == 2:
    if exists(pypath + '/' + sys.argv[1]): myconfigfile = sys.argv[1]

if len(sys.argv) == 3:
    if exists(pypath + '/' + sys.argv[1]): myconfigfile = sys.argv[1]
    if exists(pypath + '/' + sys.argv[2]): myconfigfile = sys.argv[2]
    if '-noaction' in [sys.argv[1], sys.argv[2]]: flg_action = False

# read configuration file
config = configparser.ConfigParser()
config.read(pypath + '/' + myconfigfile)

temppath    = config['GENERAL']['temppath']
mailserver  = config['IMAP']['mailserver']
mailpwd     = config['IMAP']['mailpwd']
mailaddress = config['IMAP']['mailaddress']

try: printername = config['PRINTER']['printername']
except KeyError: printername = ''

try: whitelist   = config['IMAP']['whitelist'].replace(' ','').split(',')
except KeyError: whitelist = ''

try: encryptpwd = (config['IMAP']['encryptpwd'] == 'True')
except KeyError: encryptpwd = True

if encryptpwd == True:
    mac_key     = macpassencrypt.get_mackey(False)
    mailpwd     = macpassencrypt.password_decrypt(mailpwd.encode(), mac_key).decode()

if printername == '':
    str_printer = '' # use default printer
else:
    str_printer = '-d ' + printername + ' '

# some preparations
filepath = pypath + '/' + temppath + '/'
uidlist  = []
filelist = []

# fetch mails with '#drucken' or '#print' in subject from mailbox, save attachments and delete these mails again
with MailBox(mailserver).login(mailaddress,mailpwd) as mailbox:
    
    for msg in mailbox.fetch(criteria=OR(AND(subject='#print', seen=False), AND(subject='#drucken', seen=False)), mark_seen=False, bulk=True):
        if not whitelist == '' and not msg.from_.lower() in whitelist: continue # skip msg if not from whitelist
        uidlist += [msg.uid]
        for att in msg.attachments:
            #print(msg.uid, msg.date, msg.from_, msg.subject, att.filename, att.content_type)
            if att.filename == '': continue
            filelist += [[msg.uid, msg.date, msg.from_, msg.subject, att.filename, att.content_type]] # write subjects and filenames to list 
            with open(filepath + att.filename, 'wb') as f:
                f.write(att.payload)

    # delete mails again
    if flg_action: mailbox.delete(uidlist)

# clear imap information from memory
del mailserver, mailaddress, mailpwd, whitelist

# print attachments
for myatt in filelist:

    [uid, date, from_, subject, filename, content_type] = myatt            
    
    # default printing choices
    flg_duplex      = True
    flg_2on1        = False
    flg_pageextract = False
    flg_landscape   = False
    nup             = 1
    
    # replace #seiten by #pages (if exists)
    try: subject = subject.replace('#pages','#seiten')
    except ValueError: pass
        
    # find keys in subject line    
    keys_2on1     = ['#2on1', '#2auf1']
    keys_duplex   = ['#duplex', '#twosided', '#beidseitig', '#2seitig']
    keys_noduplex = ['#noduplex', '#singlesided', '#einseitig', '#1seitig']
    
    if any(key in subject for key in keys_2on1)    : flg_2on1   = True
    if any(key in subject for key in keys_duplex)  : flg_duplex = True
    if any(key in subject for key in keys_noduplex): flg_duplex = False
    
    # number of pages per sheet
    if flg_2on1: nup = 2
    str_nup = '-o number-up=' + str(nup) + ' '
    
    # get extract pages
    str_pages   = ''
    subj_split = subject.split(' ')
    try: str_pages   = subj_split[['#pages' in tmp for tmp in subj_split].index(True)].replace('#pages','')
    except ValueError: pass

    # convert to pdf: check file type (allowed types: pdf, docx, pptx, text-file)
    str_file = filepath + filename
    filename_noextension, file_extension = os.path.splitext(str_file)
    
    # converting/preparing binary files
    if is_binary(str_file) or file_extension == '.pdf':
        
        # convert non-pdfs
        if not file_extension == '.pdf':
            stream = os.popen('unoconv -f pdf -o "' + str_file + '.pdf" "' + str_file + '"')
            str_file = str_file + '.pdf' # append .pdf
            if 'UnoException' in stream.read():
                continue # go to next iteration
                
        # check orientation
        if pdf_orientation(str_file) == 'landscape':
            flg_landscape = True
            
        # extract pages
        if not str_pages == '':
            #os.system('qpdf --replace-input --pages . ' + str_pages + ' -- "' + str_file + '"') # works only with newer versions of qpdf
            
            os.system('qpdf "' + str_file + '" --pages . ' + str_pages + ' -- "' + str_file + '__tmp"') # works also with older versions of qpdf
            os.system('rm "' + str_file + '"')
            os.system('mv "' + str_file + '__tmp" "' + str_file + '"')
            
    else:
        pass # text files behave just like portrait pdf
    
    # duplex and multiple pages and orientation
    if flg_duplex:
        if flg_2on1: flg_landscape = not flg_landscape # flip orientation
        if flg_landscape:
            str_duplexorientation = '-o sides=two-sided-short-edge '
        else:
            str_duplexorientation = '-o sides=two-sided-long-edge '
    else:
        str_duplexorientation = ''
    
    # print pdf/text
    str_command = 'lp ' + str_printer + '-o fit-to-page ' + str_nup + str_duplexorientation + '"' + str_file + '"'
    print(lenfill(str(date),27) + lenfill(from_,30) + lenfill(str_pages,8) + ' : ' + str_command) # CHECK whether this works if spaces in file/folder name
    if flg_action: os.system(str_command)
 
# delete temporary files again
if flg_action and len(filelist)>0: os.system('rm ' + filepath + '*')
