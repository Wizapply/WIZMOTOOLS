import xp
import wizmo
import time
import threading


class PythonInterface:
    """
    XPluginStart

    Our start routine registers our window and does any other initialization we
    must do.
    """

    def XPluginStart(self):
        """
        First we must fill in the passed in buffers to describe our
        plugin to the plugin-system."""
        self.Name = "WIZMO_XplaneSystem v1.0"
        self.Sig = "wizapply.wizmo.xppython"
        self.Desc = "A Simple 6DOF WIZMO-Sim plugin for the Python Interface."
        self.Clicked = False
        self.counter = 0
        """
        Now we create a window.  We pass in a rectangle in left, top,
        right, bottom screen coordinates.  We pass in three callbacks."""
        windowInfo = (50, 600, 300, 400, 1,
                      self.DrawWindowCallback,
                      self.MouseClickCallback,
                      self.KeyCallback,
                      self.CursorCallback,
                      self.MouseWheelCallback,
                      0,
                      xp.WindowDecorationRoundRectangle,
                      xp.WindowLayerFloatingWindows,
                      None)
        self.WindowId = xp.createWindowEx(windowInfo)

        try:
            self.wm = wizmo.wizmo(True)
            self.wm.starter('')

            while self.wm.get_status() == wizmo.wizmoStatus.Initial:
                time.sleep(0.1)    #wait 0.1s
            logstr =  self.wm.get_backlog()
            print(logstr)
            authcheck = 'Successfully authenticated the WIZMO.' in logstr
            simcheck = 'Successfully connected to the machine.' in logstr
            if simcheck == True:
                if authcheck == True:
                    self.Desc = "WIZMO is Opened."
                    self.wm.speed_gain_mode(True)
                else:
                    self.Desc = "Machine is not authenticated."
            else:
                self.Desc = "There is no machine available."
            # print("wizmo Open")
        except FileNotFoundError:
            self.Desc = "WIZMO DLL NOT FOUND ERROR!"

        #DataRef
        self.DataRef_phi = xp.findDataRef("sim/flightmodel/position/phi")
        self.DataRef_psi = xp.findDataRef("sim/flightmodel/position/psi")
        self.DataRef_theta = xp.findDataRef("sim/flightmodel/position/theta")
        self.DataRef_local_ax = xp.findDataRef("sim/flightmodel/position/local_ax")
        self.DataRef_local_ay = xp.findDataRef("sim/flightmodel/position/local_ay")
        self.DataRef_local_az = xp.findDataRef("sim/flightmodel/position/local_az")

        self.preYaw = 0
        self.firstFrameFlg = False
        return self.Name, self.Sig, self.Desc

        

    """
    XPluginStop

    Our cleanup routine deallocates our window.
    Thing you create, register in "Start" should be destroyed, unregistered in "Stop"
    """
    def XPluginStop(self):
        xp.destroyWindow(self.WindowId)
        self.wm.close()

    """
    XPluginEnable.

    We don't do any enable-specific initialization, but we must return 1 to indicate
    that we may be enabled at this time.
    """
    def XPluginEnable(self):
        return 1

    """
    XPluginDisable

    We do not need to do anything when we are disabled, but we must provide the handler.
    Similar to Start/Stop, things you create / register in Enable should be
    destroyed / unregistered in Disable
    """
    def XPluginDisable(self):
        pass

    """
    XPluginReceiveMessage

    We don't have to do anything in our receive message handler, but we must provide one.
    """
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass

    """
    MyDrawingWindowCallback

    This callback does the work of drawing our window once per sim cycle each time
    it is needed.  It dynamically changes the text depending on the saved mouse
    status.  Note that we don't have to tell X-Plane to redraw us when our text
    changes; we are redrawn by the sim continuously.
    """
    def DrawWindowCallback(self, inWindowID, inRefcon):
        # First we get the location of the window passed in to us.
        (left, top, right, bottom) = xp.getWindowGeometry(inWindowID)
        """
        We now use an XPLMGraphics routine to draw a translucent dark
        rectangle that is our window's shape.
        """
        xp.drawTranslucentDarkBox(left, top, right, bottom)
        color = 1.0, 1.0, 1.0

        # if self.Clicked:
        #     Desc = "I'm a plugin 1"
        # else:
        #     Desc = "Hello World WIZAPPLY"
        # self.rollparam = xp.getDataf(self.DataRef)
        self.pitchparam = round(xp.getDataf(self.DataRef_theta),2) / 10.0
        self.rollparam = round(xp.getDataf(self.DataRef_phi),2) / 10.0
        self.nowYaw = round(xp.getDataf(self.DataRef_phi),2)

        if self.firstFrameFlg == False:
            self.yawparam = 0
            self.firstFrameFlg = True
        else:
            self.yawparam = self.nowYaw - self.preYaw

        self.heaveparam = round(xp.getDataf(self.DataRef_local_ay),2) / 10.0
        self.swayparam = round(xp.getDataf(self.DataRef_local_ax),2) / 10.0
        self.surgeparam = round(xp.getDataf(self.DataRef_local_az),2) / 10.0

        if self.wm.get_status() == wizmo.wizmoStatus.Running:
            self.wm.simple_pose_update(self.rollparam,self.pitchparam,self.yawparam,self.heaveparam,self.swayparam,self.surgeparam)
            logstr =  self.wm.get_backlog()
            # time.sleep(0.1) #100ms
        else:
            logstr =  'WIZMO is Not Running'

        
        self.preYaw = self.nowYaw
        """
        Finally we draw the text into the window, also using XPLMGraphics
        routines.  The NULL indicates no word wrapping.
        """
        xp.drawString(color, left + 5, top - 20, self.Desc, 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 40, logstr, 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 60, 'pitch : ' + format(self.pitchparam,'.3f'), 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 80, 'roll : ' + format(self.rollparam,'.3f'), 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 100, 'yaw : ' + format(self.yawparam,'.3f'), 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 120, 'heave : ' + format(self.heaveparam,'.3f'), 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 140, 'sway : ' + format(self.swayparam,'.3f'), 0, xp.Font_Basic)
        xp.drawString(color, left + 5, top - 160, 'surge : ' + format(self.surgeparam,'.3f'), 0, xp.Font_Basic)
    """
    MyHandleKeyCallback

    Our key handling callback does nothing in this plugin.  This is ok;
    we simply don't use keyboard input.
    """
    def KeyCallback(self, inWindowID, inKey, inFlags, inVirtualKey, inRefcon, losingFocus):
        pass

    """
    MyHandleMouseClickCallback

    Our mouse click callback toggles the status of our mouse variable
    as the mouse is clicked.  We then update our text on the next sim
    cycle.
    """
    def MouseClickCallback(self, inWindowID, x, y, inMouse, inRefcon):
        """
        If we get a down or up, toggle our status click.  We will
        never get a down without an up if we accept the down.
        """
        if inMouse in (xp.MouseDown, xp.MouseUp):
            self.Clicked = not self.Clicked

        """
        Returning 1 tells X-Plane that we 'accepted' the click; otherwise
        it would be passed to the next window behind us.  If we accept
        the click we get mouse moved and mouse up callbacks, if we don't
        we do not get any more callbacks.  It is worth noting that we
        will receive mouse moved and mouse up even if the mouse is dragged
        out of our window's box as long as the click started in our window's
        box.
        """
        return 1

    def CursorCallback(self, inWindowID, x, y, inRefcon):
        """
        Cursor Callback, you must return XPLMCursorStatus to indicate how to
        display the cursor.
        """
        return xp.CursorDefault

    def MouseWheelCallback(self, inWindowID, x, y, wheel, clicks, inRefcon):
        """
        return 1 to consume the mouse wheel movement, 0 to pass them to lower window.
        (If you window appears opaque to the user, you should consume the mouse wheel
        scolling, even if it does nothing.)
        """
        return 1
