#!/usr/bin/env python
#
import os
import rospy
import rospkg
import rosservice

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget

from jsk_gui_msgs.srv import YesNo, YesNoResponse


class YesNoButtonWidget(QWidget):
    def __init__(self):
        super(YesNoButtonWidget, self).__init__()
        rp = rospkg.RosPack()
        ui_file = os.path.join(rp.get_path('jsk_rqt_plugins'),
            'resource', 'yes_no_button.ui')
        loadUi(ui_file, self)
        self.setObjectName('YesNoButtonUi')
        self.yes_button.clicked[bool].connect(self._clicked_yes_button)
        self.no_button.clicked[bool].connect(self._clicked_no_button)
        self.yes_button.setEnabled(False)
        self.no_button.setEnabled(False)
        self.yes = None
        service_name = rospy.get_namespace() + 'rqt_yn_btn'
        if service_name in rosservice.get_service_list():
            rospy.logwarn('{} is already advertised'.format(service_name))
            return
        self.srv = rospy.Service('rqt_yn_btn', YesNo, self._handle_yn_btn)

    def _clicked_yes_button(self):
        """Handle events of being clicked yes button."""
        self.yes = True

    def _clicked_no_button(self):
        """Handle events of being clicked no button."""
        self.yes = False

    def _handle_yn_btn(self, req):
        """Callback function of service,
        and handle enable/disable of the buttons."""
        self.message.setText(req.message)
        self.yes = None  # initialize
        self.yes_button.setEnabled(True)
        self.no_button.setEnabled(True)
        while self.yes is None:  # wait for user input
            rospy.sleep(1.)
        self.yes_button.setEnabled(False)
        self.no_button.setEnabled(False)
        return YesNoResponse(yes=self.yes)

    def __del__(self):
        self.srv.shutdown()


class YesNoButton(Plugin):
    def __init__(self, context):
        super(YesNoButton, self).__init__(context)
        self.setObjectName('YesNoButton')
        self._widget = YesNoButtonWidget()
        context.add_widget(self._widget)
