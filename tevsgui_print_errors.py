import gtk
import pdb
import pango

class PrintErrors(object):
    def __init__(self,error_file,window):
        self.error_file = error_file 
        self.page_starts = []
        self.line_array = []
        self.paginated_pages = 0
        self.window = window
        print_op = gtk.PrintOperation()
        print_op.connect("begin_print",self.begin_print,None)
        print_op.connect("paginate",self.paginate,None)
        print_op.connect("request_page_setup",self.request_page_setup,None)
        print_op.connect("draw_page",self.draw_page,None)
        print_op.connect("end_print",self.end_print,None)
        res = print_op.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, self.window)

    def begin_print(self,printop,context,data):
        pass

    def end_print(self,printop,context,data):
        pass

    def request_page_setup(self,printop,context,page_number,setup,data):
        pass

    def paginate(self,printop,context,data):
        """ paginate """
        # For some reason, paginate gets called twice.
        if self.paginated_pages > 0:
            return True
        line_count = 0
        efile = open(self.error_file,"r")
        for line in efile.readlines():
            try:
                if line.find("ERR")>-1:
                    self.line_array.append(line[:-1])
                    if (line_count % 40)==0:
                        self.page_starts.append(line_count)
                        print self.page_starts
                    line_count += 1
            except Exception, e:
                print e
        self.page_starts.append(line_count)
        print self.page_starts
        self.paginated_pages = len(self.page_starts)-1
        print "Page starts",self.page_starts
        print self.paginated_pages
        printop.set_n_pages(self.paginated_pages)
        return True

    def draw_page(self,printop,context,page_number,data):
        #print "****Draw Page",page_number
        #print "Printop",printop
        #print "Context",context
        #print "Page number",page_number
        #print "Data for this page"
        
        try:
            start = self.page_starts[page_number]
        except:
            return
        try:
            end = self.page_starts[page_number+1]
        except:
            end = len(self.line_array)
        if start > end:
            return
            
        textarray = []
        header = "<big>Errors in extraction log, page %d of %d.\n</big>" % (
            page_number+1,
            len(self.page_starts)-1)

        textarray.append(header)
            
        for index in range(start,end):
            textarray.append(self.line_array[index])
        if end == len(self.line_array):
            textarray.append(" ")
            textarray.append("Errors from extraction log ENDS")

        cr = context.get_cairo_context()
        width = context.get_width()
        layout = context.create_pango_layout()
        desc = pango.FontDescription("monospace 10")
        layout.set_font_description(desc)
        layout.set_width(-1)
        layout.set_markup("\n".join(textarray))
        layout.set_alignment(pango.ALIGN_LEFT)
        x,layout_height = layout.get_size()
        print layout.get_size()
        text_height = layout_height/pango.SCALE
        cr.move_to(context.get_dpi_x()/2,context.get_dpi_y()/2)
        cr.show_layout(layout)
                        


class App(object):

    def do_print_errors(self,button,data):
        pe = PrintErrors(data[0],data[1])
        
    def do_exit(self,button,data):
        gtk.main_quit()

    def delete_event(self,widget,event,data):
        return False

    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("tevsgui_print_errors.glade")
        self.window = self.builder.get_object("windowMain")
        self.window.set_title("Print Errors Test Version")
        self.peb = self.builder.get_object("printErrorsButton")
        self.eb = self.builder.get_object("exitButton")
        self.window.connect("delete_event",
                            self.delete_event,
                            None)
        self.peb.connect("clicked",
                         self.do_print_errors,
                         ("/home/mitch/nov2011/extraction.log",self.window))    
        self.eb.connect("clicked",
                        self.do_exit, 
                        None)
                        

        
if __name__ == "__main__":
    app = App()
    app.window.show()
    gtk.main()
