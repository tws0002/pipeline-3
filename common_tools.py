








def get_hooks_module(config_reader, software):
	pass
	# hooks_path = config_reader.getHooksPath(software)
	# hooks_dir = os.path.dirname(hooks_path)
	# from __future__ import absolute_import
	# from .hooks_dir import 
	# sys.path.append(hooks_path)


# DEBUGGING------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	path = 'V:/Jobs/182276_Essilor_Out_of_Focus/Design/Production/TVC60/Assets/Environments/Gym/model/esof_gym_model_V02.ma'
	app = QtGuiWidgets.QApplication(sys.argv)
	print(version_up(path))
	# print(get_version_str(path, False))
	# print(get_version_int(path))
