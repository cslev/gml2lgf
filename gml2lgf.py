'''
    GML2LGF converter - Converts traditional gml files into Lemon Graph Format
    Copyright (C) 2013  Levente Csikor

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    For more information send an email to: csikor@tmit.bme.hu
'''
# -*- encoding: utf-8 -*-
from converter import Converter
import os

import kivy
kivy.require('1.8.0') # replace with your current kivy version !
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
#these imports are required for file chooser dialog
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window

from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
#for found params 3 different ui element should be added
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)    


class GUI(BoxLayout):
    """This class is devoted to create GUI and handle the actions"""

    
    #variable for converter class
    converter = None
    
    loadfile = ObjectProperty(None)
    selected_file = None
    path = None
    path_only = None
    lgf_name = None
    lgf_nfo = None
    
    node_params_root = None
    node_params_layout = None
    edge_params_root = None
    edge_params_layout = None
    
    
    params_width = Window.width/2
    params_height = Window.height/2.6
    
    
    
    #GUI node_params dictionary for the found node params list
    #by means of this, we can easily check after clicking Convert button that what should be
    #written in the lemon file and how
    node_params_to_write = dict()
    #and the same for edges
    edge_params_to_write = dict()
    
    
    #link costs' checkbox
    found_cost_cb = None
    random_cost_cb = None
    unit_cost_cb = None
    
    symmetric_cost_cb = None
    
    #convert button
#     convert_button = None
    lemon_req = "USE AS LEMON REQUIRES"
    
    def initialize(self):
        '''
        INITIALIZING GUI COMPONENTS
        '''
        #just for faster testing
        self.file_text_input.text = ""
     
        #initializing node_params scrollview and layout
        self.node_params_layout = GridLayout(cols=2,spacing=10, size_hint_y=None)
        self.node_params_layout.bind(minimum_height=self.node_params_layout.setter('height'))
        
        self.node_params_root = ScrollView(size_hint=(None, None), 
                                           size=(self.params_width,self.params_height),
                                           bar_width=5,
                                           bar_color=[.3,.3,.9,.5],
                                           do_scroll_x=False,
                                           )        
        self.node_params_root.add_widget(self.node_params_layout)
        #initializing edge_params scrollview and layout
        self.edge_params_layout = GridLayout(cols=2,spacing=10,size_hint_y=None)
        self.edge_params_layout.bind(minimum_height=self.edge_params_layout.setter('height'))
        self.edge_params_root = ScrollView(size_hint=(None, None), 
                                           size=(self.params_width-20,self.params_height),
                                           bar_width=5,
                                           bar_color=[.3,.3,.9,.5],
                                           do_scroll_x=False)        
        self.edge_params_root.add_widget(self.edge_params_layout)
        
        #adding params widgets
        self.params_boxlayout.add_widget(self.node_params_root)
        self.params_boxlayout.add_widget(self.edge_params_root)

        
        
    
    def dismiss_popup(self):
        """
        This dismisses popups
        """
        self._popup.dismiss()
    
    
    def show_load(self):
        """
        show load file dialog
        """
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
    
    
    def load(self, path, filename):
        """
        this will load the file and dismiss the dialog
        """

        try:
            self.selected_file = filename[0]
            self.file_text_input.text = self.selected_file
            self.dismiss_popup()
#             print "Selected file",self.selected_file
            #getting the path and the filename separately
            
            basename = os.path.basename(self.selected_file) 
            path = os.path.abspath((self.selected_file))
            
#             print "Basename",basename
            self.path_only = path[:(len(path)-len(basename))]
            basename = str(os.path.splitext(os.path.basename(self.selected_file))[0])
            #With these variable will shown where the new lgf and nfo file is saved
            self.lgf_name = self.path_only + basename  + ".lgf"
            self.lgf_nfo = self.path_only + basename + ".nfo"
            
            
#             print self.path_only
#             print self.lgf_name
#             print self.lgf_nfo
            
        except IndexError as ie:
            print ("Something made a boo-boo...try again", str(ie))  
            self.dismiss_popup()
            self.show_popup("ERROR","Somehow I couldn't load the file:\nCheck the permissions or move it to other place")
        
         
    def analyze(self):
        '''
        This function analyzes the read gml file
        '''
        self.converter = Converter(self.file_text_input.text)
        self.converter.set_reference(self.console_log)
        
        #clear console log
        self.console_log.text = ""
        #check that selected file is existing
        if(self.converter.read_file() != False):
            
            self.node_param_label.text = "Found node params (#{})".format(str(len(self.converter.node_params)))
            self.edge_param_label.text = "Found edge params (#{})".format(str(len(self.converter.edge_params)))
            
           
            
            #removing previously added widgets
            self.node_params_layout.clear_widgets()
            self.edge_params_layout.clear_widgets()
            
            
            ##### ---=========== NODE PARAMS PART    =====------- ######
            #adding the two column names
            self.node_params_layout.add_widget(Label(text="", font_size="12sp"))
            self.node_params_layout.add_widget(Label(text="", font_size="12sp"))
            self.node_params_layout.add_widget(Label(text="Property name in [b]GML[/b]", font_size="14sp",markup=True))
            self.node_params_layout.add_widget(Label(text="Property name in [b]LGF[/b]", font_size="14sp",markup=True))
            
            
            
            
            #adding found paramters to the related params widgets
            for i in self.converter.node_params:
                #LEMON uses label for ids
                if(str(i) == "id"):
                    textinput = TextInput(text = "label", 
                                          multiline=False,
                                          size_hint_x=0.6, 
                                          size_hint_y=None, 
                                          height=28, 
                                          font_size=12,
                                          readonly=True,
                                          foreground_color=[.9,.1,.1,1],
                                          background_color=[.7,.7,.7,1])
                elif(str(i) == "label"):
                    textinput = TextInput(text = "name", 
                                          multiline=False,
                                          size_hint_x=0.6, 
                                          size_hint_y=None, 
                                          height=28, 
                                          font_size=12,
                                          readonly=True,
                                          foreground_color=[.9,.1,.1,1],
                                          background_color=[.7,.7,.7,1])
                else:
                    textinput = TextInput(text = str(i).lower(), 
                                          multiline=False,
                                          size_hint_x=0.6, 
                                          size_hint_y=None, 
                                          height=28, 
                                          font_size=12)
                
                self.node_params_to_write[str(i)]=textinput
              
#             print(self.node_params_to_write)  
            for i in self.node_params_to_write:       
                if(self.converter.node_params[i] != len(self.converter.nodes)):          
                    label_text = "[b][color=ffff00]"+str(i) + "[/color][/b] --->"
                else:
                    label_text = "[b]"+str(i) + "[/b] --->"
                label = Label(text=label_text,
                              size_hint_x=0.4, 
                              size_hint_y=None, 
                              height=28, 
                              font_size="12sp",
                              markup=True)
                self.node_params_layout.add_widget(label)
                self.node_params_layout.add_widget(self.node_params_to_write[i])
            ##### ---======= END OF NODE PARAMS PART =====------- ######
        
        
        
        
        
            ##### ---=========== EDGE PARAMS PART    =====------- ######
            #adding the two column names
            self.edge_params_layout.add_widget(Label(text="", font_size="12sp"))
            self.edge_params_layout.add_widget(Label(text="", font_size="12sp"))
            self.edge_params_layout.add_widget(Label(text="Property name in [b]GML[/b]", font_size="14sp",markup=True))
            self.edge_params_layout.add_widget(Label(text="Property name in [b]LGF[/b]", font_size="14sp",markup=True))

            #adding found paramters to the related params widgets
            for i in self.converter.edge_params:
                #LEMON uses label for ids
                if((str(i) == "source") or (str(i) == "target")):
                    textinput = TextInput(text = self.lemon_req, 
                                          multiline=False,
                                          size_hint_x=0.6, 
                                          size_hint_y=None, 
                                          height=28, 
                                          font_size=12,
                                          readonly=True,
                                          foreground_color=[.9,.1,.1,1],
                                          background_color=[.7,.7,.7,1])
                elif((str(i) == "id") or (str(i) == "label")):
                    textinput = TextInput(text = "name", 
                                          multiline=False,
                                          size_hint_x=0.6, 
                                          size_hint_y=None, 
                                          height=28, 
                                          font_size=12)
                else:
                    textinput = TextInput(text = str(i).lower(), 
                                          multiline=False,
                                          size_hint_x=0.6, 
                                          size_hint_y=None, 
                                          height=28, 
                                          font_size=12)
                    
                self.edge_params_to_write[str(i)]=textinput
            for i in self.edge_params_to_write:       
                if(self.converter.edge_params[i] != len(self.converter.edges)):          
                    label_text = "[b][color=ffff00]"+str(i) + "[/color][/b] --->"
                else:
                    label_text = "[b]" + str(i) + "[/b] --->"
                label = Label(text=label_text,
                              size_hint_x=0.4, 
                              size_hint_y=None, 
                              height=28, 
                              font_size="12sp",
                              markup=True)
                self.edge_params_layout.add_widget(label)
                self.edge_params_layout.add_widget(self.edge_params_to_write[i])
            
            
            #adding checkboxes for link costs                        
            self.found_cost_cb = CheckBox(size_hint=(.9,None),group="link_costs",height=12,active=True)
#             found_cost_cb.bind(active=self.on_checkbox_active)
            self.random_cost_cb = CheckBox(size_hint=(.9,None),group="link_costs",height=12)
#             random_cost_cb.bind(active=self.on_checkbox_active)
            self.unit_cost_cb = CheckBox(size_hint=(.9,None),group="link_costs",height=12)
#             unit_cost_cb.bind(active=self.on_checkbox_active)
            
           
            #adding checkboxes to GUI
            self.edge_params_layout.add_widget(Label(text="Found link costs",halign="justify"))
            self.edge_params_layout.add_widget(self.found_cost_cb)
            self.edge_params_layout.add_widget(Label(text="Random[1,100] link costs",halign="justify"))
            self.edge_params_layout.add_widget(self.random_cost_cb)
            self.edge_params_layout.add_widget(Label(text="Unit link costs",halign="justify"))
            self.edge_params_layout.add_widget(self.unit_cost_cb)
            
            
            #adding symmetric link costs option to GUI
            self.symmetric_cost_cb = CheckBox(size_hint=(.9,None),height=14,paddint=10,active=True)
            self.edge_params_layout.add_widget(Label(text="", font_size="14sp"))
            self.edge_params_layout.add_widget(Label(text="", font_size="14sp"))
            self.edge_params_layout.add_widget(Label(text="Use symmetric costs"))
            self.edge_params_layout.add_widget(self.symmetric_cost_cb)
#             self.edge_params_layout.add_widget(Label(text="(Lemon DiGraph)",size_hint=(None,None),height=8))
            
            
            ##### ---======= END OF EDGE PARAMS PART =====------- ######
#           
    
        else:
#             self.show_popup("ERROR", "Unable to read file: {}".format(self.file_text_input.text))
            self.show_popup("ERROR", self.converter.error_msg)

#     def on_checkbox_active(self,checkbox,value):
#         
#         print value

    def dummy(self):
        print("GML2LGF converter gui started")
        
        
    def convert(self):
        """This function checks whether everything was set and read correctly,
        and then calls Converter class' dedicated functions to write out
        the new LGF file"""
        
        #checking that analyze button was pressed and some gml file was already loaded  
        if isinstance(self.converter, Converter):
            #OK, we can do convert now, all necessary stuff was created and file was read
            
            status = dict()
            print ("CONVERT")     
            if(self.found_cost_cb.active):
                status["cost"] = "found"
            elif(self.random_cost_cb.active):
                status["cost"] = "random"   
            elif(self.unit_cost_cb.active):
                status["cost"] = "unit"
            else:
                self.show_popup("ERROR", "Somehow the type of costs was not selected")    
             
            status["symmetric"] = False
            if(self.symmetric_cost_cb.active):
                   status["symmetric"] = True
                
            #HERE we call the Converter class' function to finalize the results
            node_params_to_write_with_given_paramname = dict()
            for i in self.node_params_to_write:
                if(self.node_params_to_write[i].text != ""):
                    node_params_to_write_with_given_paramname[i] = self.node_params_to_write[i].text
                    
            
            #HERE we get the set parameters for the edges
            edge_params_to_write_with_given_paramname = dict()
            for i in self.edge_params_to_write:
                if(self.edge_params_to_write[i].text != self.lemon_req):
                    edge_params_to_write_with_given_paramname[i] = self.edge_params_to_write[i].text
                
            self.converter.write_out_results(status,
                                             node_params_to_write_with_given_paramname,
                                             edge_params_to_write_with_given_paramname)
            
        
            self.show_popup("DONE","The new .lgf and .nfo file is created\n"+str(self.lgf_name)+"\n"+str(self.lgf_nfo))
#             print "The new .lgf and .nfo file is created\n"+str(self.lgf_name)+"\n"+str(self.lgf_nfo)
        else:
            print ("No file was loaded and analyze --- do it first")
            self.show_popup("ERROR", "No GML file was loaded and analyzed\n DO IT FIRST!")
         
        
            
        
    def show_popup(self,*args):
        """This functions shows a Kivy Popup window"""
        
        popup = Popup(title=args[0],
                      content=Label(text=args[1]),
                      size_hint=(None,None), 
                      size=(Window.width-50,Window.height-50),
                      separator_color=[247 / 255., 1 / 255., 1 / 255., 1.],
                      title_size='24sp')
        popup.open()
        

    def get_filetext_input(self):
        """reads the text of the file input text_field"""
        return self.file_txt_input
    
    
    def close(self):
        """Default close event to main window"""
        exit()
   
class Gml2LgfApp(App):
    """The main class"""
    title = "GML2LGF converter"
    #this is also important for file chooser dialog
    Factory.register('LoadDialog', cls=LoadDialog)
    icon = 'GML2LGF_ICON.png'    
    def build(self):
        self.gui = GUI()    #instatiate main Gml2Lgf class
        self.gui.initialize()
        self.gui.dummy()

        
        #event handling window resize
        def win_cb(window,width,height):
            self.gui.params_width = Window.width/2
            self.gui.params_height = Window.height/2.6
            self.gui.node_params_root.size=(self.gui.params_width,self.gui.params_height)
            self.gui.edge_params_root.size=(self.gui.params_width-20,self.gui.params_height)
            print("resizing:{}".format(window.height))
            
        Window.bind(on_resize=win_cb)    
        return self.gui
    
if __name__ == '__main__':Gml2LgfApp().run()
