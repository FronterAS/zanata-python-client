#vim:set et sts=4 sw=4:
#
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@redhat.com>
# Copyright (c) 2010 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

__all__ = (
            "FliesConsole",
        )

import getopt, sys
import os.path
from flieslib import *
from flieslib.error import *
from parseconfig import FliesConfig
from publicanutil import PublicanUtility

sub_command = {
                'help':[],
                'list':[],
                'status':[],
                'project':['info','create', 'remove'],
                'version':['info', 'create', 'remove'],
                'publican':['push', 'pull']
                }

options = {
            'url' : '',
            'user_name':'',
            'key':'',
            'user_config':'',
            'project_config':'',
            'project_id':'',
            'project_version':'',
            'srcdir':'',
            'dstdir':'',
            'transdir':'',
            'project_name':'',
            'project_desc':'',
            'version_name':'',
            'version_desc':'',
            'lang':'',
            'email':'',
            'importpo':False,
            'copytrans':True
            }

class FliesConsole:

    def __init__(self):
        self.client_version = "0.8.1"        
        self.url = ''
        self.user_name = ''
        self.apikey = ''
        self.user_config = ''
        self.project_config = {'project_url':'', 'project_id':'', 'project_version':'', 'locale_map':{}}
        self.force = False
        self.log = Logger()
        
    def _print_usage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'Usage: flies <command> [COMMANDOPTION]...\n\n'
               'list of commands:\n'
               ' list                List all available projects\n'
               ' project info        Show information about a project\n'
               ' version info        Show information about a version\n'
               ' project create      Create a project\n'
               ' version create      Create a version within a project\n'
               ' publican pull       Pull the content of publican file\n'
               ' publican push       Push the content of publican file to Flies server\n'
               "Use 'flies help' for the full list of commands")

    def _print_help_info(self, args):
        """
        Output the general help information or the help information for each command
        @param args: the name of command and sub command
        """
        if not args:
            print ('Client for talking to a Flies Server:\n\n'
                  'Usage: flies <command> [COMMANDOPTION]...\n\n'
                  'list of commands:\n'
                  ' help                Display this help and exit\n'
                  ' list                List all available projects\n'
                  ' project info        Show information about a project\n'
                  ' version info        Show information about a version\n'
                  ' project create      Create a project\n'
                  ' version create      Create a version within a project\n'
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican file to Flies server\n')
        else:
            command = args[0]
            sub = args[1:]
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                        else:
                            self.log.error("Can not find such command")
                            sys.exit(1)
            else:
                self.log.error("Can not find such command")
                sys.exit(1)

            self._command_help(command)

    def _command_help(self, command):      
        if command == 'list':
            self._list_help()
        elif command == 'project':
            print ("Command:'flies project info'\n"
                   "        'flies project create'")
        elif command == 'project_info':
            self._projec_info_help()
        elif command == 'project_create':
            self._project_create_help()
        elif command == 'version':
            print ("Command:'flies version info'\n"
                   "        'flies version create'")
        elif command == 'version_info':
            self._iteration_info_help()
        elif command == 'version_create':
            self._iteration_create_help()
        elif command == 'publican':
            print ("Command:'flies publican push'\n"
                   "        'flies publican pull'")
        elif command == 'publican_push':
            self._publican_push_help()
        elif command == 'publican_pull':
            self._publican_pull_help()

    def _list_help(self):
       	print ('flies list [OPTIONS]\n'
               'list all available projects\n'
               'options:\n'
               ' --url address of the Flies server, eg http://example.com/flies')
    
    def _projec_info_help(self):
	    print ('flies project info [OPTIONS]\n'
               'show infomation about a project\n'
               'options:\n'
               '--project-id: project id')

    def _project_create_help(self):
        print ('flies project create [PROJECT_ID] [OPTIONS]\n'
               'create a project\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-name: project name\n'
               '--project-desc: project description')

    def _iteration_info_help(self):
	    print ('flies version info [OPTIONS]\n'
               'show infomation about a version\n'
               'options:\n'
               '--project-id: project id\n'
               '--project-version: id of project version')

    def _iteration_create_help(self):
        print ('flies version create [VERSION_ID] [OPTIONS]\n'
               'create a version\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--version-name: version name\n'
               '--version-desc: version description')

    def _publican_push_help(self):
        print ('flies publican push [OPTIONS] {documents}\n'
               'push the publican files to flies server\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--project-version: id of the version\n'
               '--srcdir: the full path of the pot folder\n'
               '--transdir: the full path of the folder that contain locale folders\n'
               '--import-po: push the translation at the same time\n'
               '--no-copytrans: disable flies server to copy translation from other versions')

    def _publican_pull_help(self):
        print ('flies publican pull [OPTIONS] {documents} {lang}\n'
               'retrieve the publican files from flies server\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--project-version: id of the version\n'
               '--dstdir: the path of the folder for saving the po files\n'
               '--lang: language list')
              
    def _list_projects(self):
        """
        List the information of all the project on the flies server
        """
        flies = FliesResource(self.url)
        projects = flies.projects.list()
        
        if not projects:
            self.log.error("There is no projects on the server or the server not working")
            sys.exit(1)
        for project in projects:
            print ("\nProject Id:          %s")%project.id
            print ("Project Name:        %s")%project.name
            print ("Project Type:        %s")%project.type
            print ("Project Links:       %s\n")%[{'href':link.href, 'type':link.type, 'rel':link.rel} for link in project.links]
        
    def _get_project(self):
        """
        Retrieve the information of a project
        """
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']        
        
        if not project_id:
            self.log.error('Please use flies project info --project-id=project_id or flies.xml to specify the project id')
            sys.exit(1)
      
        flies = FliesResource(self.url)
        try:
            p = flies.projects.get(project_id)
            print ("Project Id:          %s")%p.id 
            print ("Project Name:        %s")%p.name 
            print ("Project Type:        %s")%p.type
            print ("Project Description: %s")%p.description
        except NoSuchProjectException, e:
            self.log.error("There is no Such Project on the server")
        except InvalidOptionException, e:
            self.log.error("Options are not valid")
               
    def _get_iteration(self):
        """
        Retrieve the information of a project iteration.
        """
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = self.project_config['project_version']

        if not iteration_id or not project_id:
            self.log.error("Please use flies version info --project-id=project_id --project-version=project_version to retrieve the version")
            sys.exit(1)
        
        flies = FliesResource(self.url)
        try:
            project = flies.projects.get(project_id)
            iteration = project.get_iteration(iteration_id)
            print ("Version Id:          %s")%iteration.id
            print ("Version Name:        %s")%iteration.name
            print ("Version Description: %s")%iteration.description
        except NoSuchProjectException, e:
            self.log.error("There is no such project or version on the server")

    def _create_project(self, args):
        """
        Create project with the project id, project name and project description
        @param args: project id
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            self.log.error("Please provide username and apikey in flies.ini or by command line options --username and --apikey")
            sys.exit(1)
        self.log.info("Username: %s"%self.user_name)

        if not args:
            self.log.error("Please provide PROJECT_ID for creating project")
            sys.exit(1)

        if not options['project_name']:
            self.log.error("Please provide Project name by '--project-name' option")
            sys.exit(1)
       
        try:
            item = {'id':args[0], 'name':options['project_name'], 'desc':options['project_desc']}
            p = Project(item)
            result = flies.projects.create(p)
            if result == "Success":
                self.log.info("Success create the project: %s"%args[0])
        except NoSuchProjectException, e:
            self.log.error(e.msg) 
        except UnAuthorizedException, e:
            self.log.error(e.msg)
        except ProjectExistException, e:
            self.log.error(e.msg)

    def _create_iteration(self, args):
        """
        Create version with the version id, version name and version description 
        @param args: version id
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            self.log.error("Please provide username and apikey in flies.ini or by --username and --apikey options")
            sys.exit(1)

        self.log.info("Username: %s"%self.user_name)
        
        if options['project_id']:
            project_id =  options['project_id'] 
        elif self.project_config['project_id']:
            project_id = self.project_config['project_id']
        else:
            self.log.error("Please provide PROJECT_ID by --project-id option or using flies.xml")
        
        self.log.info("Project id:%s"%project_id)
        
        if not args:
            self.log.error("Please provide ITERATION_ID for creating iteration")
            sys.exit(1)

        if not options['version_name']:
            self.log.error("Please provide Iteration name by '--version-name' option")
            sys.exit(1)
         
        try:
            item = {'id':args[0], 'name':options['version_name'], 'desc':options['version_desc']}
            iteration = Iteration(item)
            result = flies.projects.iterations.create(project_id, iteration)
            if result == "Success":
                self.log.info("Success create the version %s"%args[0])
        except ProjectExistException, e:
            self.log.error(e.msg)
        except NoSuchProjectException, e:
            self.log.error(e.msg)
        except UnAuthorizedException, e:
            self.log.error(e.msg)
        except InvalidOptionException, e:
            self.log.error(e.msg)

    def check_project(self, fliesclient):
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = self.project_config['project_version']

        if not project_id:
            self.log.error("Please provide valid project id by flies.xml or by '--project-id' option")
            sys.exit(1)
        
        if not iteration_id:
            self.log.error("Please provide valid version id by flies.xml or by '--project-version' option")
            sys.exit(1)
        
        self.log.info("Project: %s"%project_id)
        self.log.info("Version: %s"%iteration_id)
        self.log.info("Username: %s"%self.user_name)

        try:
            fliesclient.projects.get(project_id)
        except NoSuchProjectException, e:
            self.log.error(e.msg)
            sys.exit(1)
   
        try:
            fliesclient.projects.iterations.get(project_id, iteration_id)
            return project_id, iteration_id
        except NoSuchProjectException, e:
            self.log.error(e.msg)
            sys.exit(1)

    def search_file(self, path, filename):
        for root, dirs, names in os.walk(path):
            if filename in names:
                return os.path.join(root, filename)
        raise NoSuchFileException('Error 404', 'File %s not found'%filename)

    def import_po(self, publicanutil, trans_folder, flies, project_id, iteration_id, filename):
        
        if options['lang']:
            lang_list = options['lang'].split(',')
        elif self.project_config['locale_map']:
            lang_list = self.project_config['locale_map'].keys()
        else:
            self.log.error("Please specify the language by '--lang' option or flies.xml")
            sys.exit(1)

        for item in lang_list:
            self.log.info("Push %s translation to Flies server:"%item)
            
            if item in self.project_config['locale_map']:
                lang = self.project_config['locale_map'][item]
            else:
                lang = item

            locale_folder = os.path.join(trans_folder, item)
                             
            if not os.path.isdir(locale_folder):
                self.log.error("Can not find translation, please specify path of the translation folder")
                continue

            if '/' not in filename:
                pofile_name = filename+'.po'
                request_name = filename
            else:
                name = filename.split('/')[1]
                pofile_name = name+'.po'
                request_name = filename.replace('/', ',')

            try:
                pofile_full_path = self.search_file(locale_folder, pofile_name)
            except NoSuchFileException, e:
                self.log.error(e.msg)
                continue
             
            body = publicanutil.pofile_to_json(pofile_full_path)

            if not body:
                self.log.error("No content or all the entry is obsolete in %s"%pofile_name)
                continue
         
            try:
                result = flies.documents.commit_translation(project_id, iteration_id, request_name, lang, body)
                if result:
                    self.log.info("Successfully pushed translation %s to the Flies server"%pofile_full_path) 
                else:
                    self.log.error("Commit translation is not successful")
            except UnAuthorizedException, e:
                self.log.error(e.msg)                                            
                break
            except BadRequestBodyException, e:
                self.log.error(e.msg)
                continue

    def update_template(self, flies, project_id, iteration_id, filename, body):
        if '/' in filename:
            request_name = filename.replace('/', ',')
        else:
            request_name = filename
        
        try:
            result = flies.documents.update_template(project_id, iteration_id, request_name, body, options['copytrans'])
            if result:
                self.log.info("Successfully updated template %s on the Flies server"%filename)
        except BadRequestBodyException, e:
            self.log.error(e.msg) 


    def _push_publican(self, args):
        """
        Push the content of publican files to a Project version on Flies server
        @param args: name of the publican file
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            self.log.error("Please provide username and apikey in flies.ini or by '--username' and '--apikey' options")
            sys.exit(1)

        project_id, iteration_id = self.check_project(flies)
        
        self.log.info("Source language: en-US")
        self.log.info("Copy previous translations:%s"%options['copytrans'])
        
        if options['importpo']:        
            self.log.info("Importing translation")
            if options['transdir']:
                trans_folder = options['transdir']
            else:
                trans_folder = os.getcwd()
            self.log.info("Read locale folders from %s"%trans_folder)            
        else:
            self.log.info("Importing source documents only")
        
        if options['srcdir']:
            tmlfolder = options['srcdir']
        else:
            tmlfolder = os.path.join(os.getcwd(), 'pot')
        
        if not os.path.isdir(tmlfolder):
            self.log.error("Can not find source folder, please specify the source folder by '--srcdir' option")
            sys.exit(1)

        self.log.info("POT directory (originals):%s"%tmlfolder)
                
        #Get the file list of this version of project
        try:
            filelist = flies.documents.get_file_list(project_id, iteration_id)
        except Exception, e:
            self.log.error(str(e))
            sys.exit(1)

        if filelist:
            #Give an option to user for keep or delete the content
            self.log.info("This will overwrite/delete any existing documents on the server.")
            
            if not self.force:
                while True:
                    option = raw_input("Are you sure (y/n)?")
                    if option.lower() == "yes" or option.lower() == "y":
                        break    
                    elif option.lower() == "no" or option.lower() == "n":
                        self.log.info("Stop processing, keep the content on the flies server")
                        sys.exit(1)
                    else:
                        self.log.error("Please enter yes(y) or no(n)")

            for file in filelist:
                if ',' in file: 
                    filename = file.replace(',', '\,')
                elif '/' in file:
                    filename = file.replace('/', ',')
                else:
                    filename = file

                self.log.info("Delete the %s"%file)
                 
                try:
                    flies.documents.delete_template(project_id, iteration_id, filename)
                except Exception, e:
                    self.log.error(str(e))
                    sys.exit(1)

        publicanutil = PublicanUtility()
        #if file not specified, push all the files in pot folder to flies server
        if not args:
            #get all the pot files from the template folder 
            pot_list = publicanutil.get_file_list(tmlfolder, ".pot")

            if not pot_list:
                self.log.error("The template folder is empty")
                sys.exit(1)

            for pot in pot_list:
                self.log.info("\nPush the content of %s to Flies server:"%pot)
                    
                body, filename = publicanutil.potfile_to_json(pot, tmlfolder)
                                          
                try:
                    result = flies.documents.commit_template(project_id, iteration_id, body, options['copytrans'])
                    if result:
                        self.log.info("Successfully pushed %s to the Flies server"%pot)    
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    break                                            
                except BadRequestBodyException, e:
                    self.log.error(e.msg)
                    continue
                except SameNameDocumentException, e:
                    self.update_template(flies, project_id, iteration_id, filename, body)

                if options['importpo']:
                    self.import_po(publicanutil, trans_folder, flies, project_id, iteration_id, filename)
            
        else:
            self.log.info("\nPush the content of %s to Flies server:"%args[0])

            try:
                full_path = self.search_file(tmlfolder, args[0])
            except NoSuchFileException, e:
                self.log.error(e.msg)
                sys.exit(1)
                        
            body, filename = publicanutil.potfile_to_json(full_path, tmlfolder)
            
            try:
                result = flies.documents.commit_template(project_id, iteration_id, body, options['copytrans'])                
                if result:
                    self.log.info("Successfully pushed %s to the Flies server"%args[0])
            except UnAuthorizedException, e:
                self.log.error(e.msg)    
            except BadRequestBodyException, e:
                self.log.error(e.msg)
            except SameNameDocumentException, e:
                self.update_template(project_id, iteration_id, filename, body)   

            if options['importpo']:
                self.import_po(publicanutil, trans_folder, flies, project_id, iteration_id, filename)

    def _pull_publican(self, args):
        """
        Retrieve the content of documents in a Project version from Flies server. If the name of publican
        file is specified, the content of that file will be pulled from server. Otherwise, all the document of that
        Project iteration will be pulled from server.
        @param args: the name of publican file
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            self.log.error("Please provide username and apikey in flies.ini or by '--username' and '--apikey' options")
            sys.exit(1)

        list = []
        if options['lang']:
            list = options['lang'].split(',')
        elif self.project_config['locale_map']:
            list = self.project_config['locale_map'].keys()
        else:
            self.log.error("Please specify the language by '--lang' option or flies.xml")
            sys.exit(1)

        project_id, iteration_id = self.check_project(flies)
        
        #list the files in project
        try:
            filelist = flies.documents.get_file_list(project_id, iteration_id)
        except Exception, e:
            self.log.error(str(e))
            sys.exit(1)

        publicanutil = PublicanUtility()
        
        #if file no specified, retrieve all the files of project
        if not args:
            if filelist:
                for file in filelist:
                    pot = ''
                    result = ''
                    folder = ''

                    if '/' in file: 
                        folder, name = file.split('/')
                    else:
                        name = file

                    self.log.info("\nFetch the content of %s from Flies server: "%name)                    
                    
                    for item in list:
                        if item in self.project_config['locale_map']:
                            lang = self.project_config['locale_map'][item]
                        else:
                            lang = item
                        
                        if options['dstdir']:
                            if os.path.isdir(options['dstdir']):
                                outpath = os.path.join(options['dstdir'], item)
                            else:
                                self.log.error("The Destination folder is not exist, please create it")
                                sys.exit(1)
                        else:
                            outpath = os.path.join(os.getcwd(), item)
                        
                        if not os.path.isdir(outpath):
                            os.mkdir(outpath)                        

                        self.log.info("Retrieve %s translation from Flies server:"%item)

                        request_name = file.replace('/', ',')

                        try:
                            pot = flies.documents.retrieve_template(project_id, iteration_id, request_name)                    
                        except UnAuthorizedException, e:
                            self.log.error(e.msg)
                            break
                        except UnAvaliableResourceException, e:
                            self.log.error("Can't find pot file for %s on Flies server"%name)
                            break
                
                        try:
                            result = flies.documents.retrieve_translation(lang, project_id, iteration_id, request_name)
                        except UnAuthorizedException, e:
                            self.log.error(e.msg)                        
                            break
                        except UnAvaliableResourceException, e:
                            self.log.info("There is no %s translation for %s"%(item, name))
                        except BadRequestBodyException, e:
                            self.log.error(e.msg)
                            continue 
                        
                        if folder:
                            subdirectory = os.path.join(outpath, folder)
                            if not os.path.isdir(subdirectory):
                                os.mkdir(subdirectory)
                            pofile = os.path.join(subdirectory, name+'.po') 
                        else:
                            pofile = os.path.join(outpath, name+'.po')
  
                        try:
                            publicanutil.save_to_pofile(pofile, result, pot)
                        except InvalidPOTFileException, e:
                            self.log.error("Can't generate po file for %s,"%name+e.msg)
        else:
            self.log.info("\nFetch the content of %s from Flies server: "%args[0])
            for item in list:
                result = ''
                pot = ''
                folder = ''

                if item in self.project_config['locale_map']:
                    lang = self.project_config['locale_map'][item]
                else:
                    lang = item
                
                if options['dstdir']:
                    if os.path.isdir(options['dstdir']):
                        outpath = os.path.join(options['dstdir'], item)
                    else:
                        self.log.error("The Destination folder is not exist, please create it")
                        sys.exit(1)
                else:
                    outpath = os.path.join(os.getcwd(), item)

                if not os.path.isdir(outpath):
                    os.mkdir(outpath)

                self.log.info("Retrieve %s translation from Flies server:"%item)

                for file in filelist:
                    if '/' in file: 
                        folder, name = file.split('/')
                        if args[0] == name:
                            request_name = file.replace('/', ',')
                            outpath = os.path.join(outpath, folder)   
                            if not os.path.isdir(outpath):
                                os.mkdir(outpath)
                            break
                    else:
                        if args[0] == file:
                            request_name = file
                            break
                
                if not request_name:
                    self.log.error("Can't find pot file for %s on Flies server"%args[0])
                    sys.exit(1)

                pofile = os.path.join(outpath, args[0]+'.po')
                                          
                try:
                    pot = flies.documents.retrieve_template(project_id, iteration_id, request_name)                    
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    sys.exit(1)
                except UnAvaliableResourceException, e:
                    self.log.error("Can't find pot file for %s on Flies server"%args[0])
                    sys.exit(1)

                try:            
                    result = flies.documents.retrieve_translation(lang, project_id, iteration_id, request_name)
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    sys.exit(1)
                except UnAvaliableResourceException, e:
                    self.log.info("There is no %s translation for %s"%(item, args[0]))
                except BadRequestBodyException, e:
                    self.log.error(e.msg)
                    continue 
      
                try:
                    publicanutil.save_to_pofile(pofile, result, pot)                    
                except InvalidPOTFileException, e:
                    self.log.error("Can't generate po file for %s,"%args[0]+e.msg)
                    
    def _remove_project(self):
        pass

    def _remove_iteration(self):
        pass

    def _project_status(self):
        pass
    
    def _process_command_line(self):
        """
        Parse the command line to generate command options and sub_command
        """
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], "vf", ["url=", "project-id=", "project-version=", "project-name=",
            "project-desc=", "version-name=", "version-desc=", "lang=",  "user-config=", "project-config=", "apikey=",
            "username=", "srcdir=", "dstdir=", "email=", "transdir=", "import-po", "no-copytrans"])
        except getopt.GetoptError, err:
            self.log.error(str(err))
            sys.exit(2)

        if args:
            command = args[0]
            sub = args[1:]            
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                            command_args = sub[1:]
                        else:
                            self.log.error("Can not find such command")
                            sys.exit(1)
                    else:
                        self.log.error("Please complete the command!")
                        sys.exit(1)
                else: 
                    command_args = sub
            else:
                self.log.error("Can not find such command")
                sys.exit(1)
        else:
            self._print_usage()
            sys.exit(1)
        
        if opts:
            for o, a in opts:
                if o =="-f":
                    self.force = True
                elif o in ("--user-config"):
                    options['user_config'] = a                     
                elif o in ("--url"):
                    options['url'] = a
                elif o in ("--project-name"):
                    options['project_name'] = a
                elif o in ("--project-desc"):
                    options['project_desc'] = a
                elif o in ("--project-id"):
                    options['project_id'] = a
                elif o in ("--version-name"):
                    options['version_name'] = a
                elif o in ("--version-desc"):
                    options['version_desc'] = a
                elif o in ("--lang"):
                    options['lang'] = a
                elif o in ("--username"):
                    options['user_name'] = a
                elif o in ("--apikey"):
                    options['key'] = a
                elif o in ("--project-config"):
                    options['project_config'] = a
                elif o in ("--project-version"): 
                    options['project_version'] = a
                elif o in ("--srcdir"):
                    options['srcdir'] = a
                elif o in ("--dstdir"):
                    options['dstdir'] = a
                elif o in ("--transdir"):
                    options['transdir'] = a
                elif o in ("--email"):
                    options['email'] = a
                elif o in ("--import-po"):
                    options['importpo'] = True
                elif o in ("--no-copytrans"):
                    options['copytrans'] = False
                   
        return command, command_args
 
    def run(self):
        command, command_args = self._process_command_line()        
        
        if command == 'help':
            self._print_help_info(command_args)
        else:
            config = FliesConfig()
            #Read the project configuration file using --project-config option
            if options['project_config']  and os.path.isfile(options['project_config']):
                self.log.info("Loading flies project config from %s"%options['project_config'])            
                self.project_config = config.read_project_config(options['project_config'])
            elif os.path.isfile(os.getcwd()+'/flies.xml'):
                #If the option is not valid, try to read the project configuration from current path
                self.log.info("Loading flies project config from from %s"%(os.getcwd()+'/flies.xml'))
                self.project_config = config.read_project_config(os.getcwd()+'/flies.xml')            
            elif command != 'list':                
                self.log.info("Can not find flies.xml, please specify the path of flies.xml")
                
            #process the url of server
            if self.project_config:
                self.url = self.project_config['project_url']
            
            #The value in options will overwrite the value in project-config file 
            if options['url']:
                self.log.info("Overwrite the url of server with command line options") 
                self.url = options['url']

            if not self.url or self.url.isspace():
                self.log.error("Please provide valid server url in flies.xml or by '--url' option")
                sys.exit(1)

            if self.url[-1] == "/":
                self.url = self.url[:-1]
                       
            #Try to read user-config file
            user_config = ''
            if options['user_config'] and os.path.isfile(options['user_config']):  
                user_config = options['user_config']
            elif os.path.isfile(os.path.expanduser("~")+'/.config/flies.ini'):
                user_config = os.path.expanduser("~")+'/.config/flies.ini'
            
            if user_config:
                self.log.info("Loading flies user config from %s"%user_config)
                
                #Read the user-config file    
                config.set_userconfig(user_config)

                try:
                    server = config.get_server(self.url)
                    if server:
                        self.user_name = config.get_config_value("username", "servers", server)
    	                self.apikey = config.get_config_value("key", "servers", server)
                except Exception, e:
                    self.log.info("Processing user-config file:%s"%str(e))
            else:    
                self.log.info("Can not find user-config file in home folder, current path or path in 'user-config' option")
            
            self.log.info("Flies server: %s"%self.url) 
            
            #The value in commandline options will overwrite the value in user-config file          
            if options['user_name']:
                self.user_name = options['user_name']
            
            if options['key']:
                self.apikey = options['key']
           
            #Retrieve the version of the Flies server 
            version = VersionService(self.url)
            
            try:            
                content = version.get_server_version()
                self.log.info("Flies python client version: %s, Flies server API version: %s"%(self.client_version, content['versionNo']))  
            except UnAvaliableResourceException, e:
                self.log.info("Flies python client version: %s"%self.client_version)
                self.log.error("Can not retrieve the server version, server may not support the version service")

            if command == 'list':
                self._list_projects()
            else:
                if command == 'status':
                    self._poject_status()
                elif command == 'project_info':
                    self._get_project()
                elif command == 'project_create':
                    self._create_project(command_args)
                elif command == 'project_remove':
                    self._remove_project(command_args)
                elif command == 'version_info':
                    self._get_iteration()
                elif command == 'version_create':
                    self._create_iteration(command_args)
                elif command == 'version_remove':
                    self._remove_iteration(command_args)
                elif command == 'publican_push':
                    self._push_publican(command_args)
                elif command == 'publican_pull':
                    self._pull_publican(command_args)

def main():
    client = FliesConsole()
    client.run()

if __name__ == "__main__":
    main()       
