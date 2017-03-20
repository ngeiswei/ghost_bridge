#
# control_psi.py - Control messages issued by the operator or pupeteer
# Copyright (C) 2016, 2017  Hanson Robotics
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import rospy
import rosmsg
import yaml
from atomic_msgs import AtomicMsgs
from dynamic_reconfigure.msg import Config


'''
    This implements a ROS node that subscribes to a mish-mash of
    control and pupeteering topics. Most of these are generated by
    the GUI control panel.  Some of these are fairly fundamental
    (turning the robot on and off) and some are hacky (fine-tuning
    misc openpsi parameters).
'''

class ControlPsi:
	def __init__(self):
		# A list of parameter names that are mirrored in opencog
		# for controling psi-rules
		self.param_list = []
		# Parameter dictionary that is used for updating states
		# recorded in the atomspace. It is used to cache the
		# atomspace values.
		self.param_dict = {}

		self.atomo = AtomicMsgs()
		rospy.Subscriber("/opencog_control/parameter_updates", Config,
			self.openpsi_control_cb)

	# For web-ui interface
	def openpsi_control_cb(self, data):
		"""
		This function is used for interactively modifying the weight of
		openpsi rules.
		"""
		param_yaml = rosmsg.get_yaml_for_msg(data.doubles + data.ints)
		self.param_list = yaml.load(param_yaml)

		for i in self.param_list:
			# Populate the parameter dictionary
			if i["name"] not in self.param_dict:
				self.param_dict[i["name"]] = i["value"]

			if i["name"] == "max_waiting_time":
				scm_str = '''(StateLink
				                 (AnchorNode "Chatbot: MaxWaitingTime")
				                 (TimeNode %f))''' % (i["value"])
			else:
				scm_str = '''(StateLink
				                 (ListLink
				                     (ConceptNode "OpenPsi: %s")
				                     (ConceptNode "OpenPsi: weight"))
				                 (NumberNode %f))''' % (i["name"], i["value"])

			self.atomo.evaluate_scm(scm_str)
