""" Wrapper for yet-to-be-written MARBL diagnostic package

Based on model_vs_obs_ecosys.py, the wrapper to Ivan Lima's python scripts
"""
from __future__ import print_function

# import core python modules
import datetime
#import errno
#import glob
import itertools
#import os
import sys
import re
#import shutil
#import traceback

# import modules installed by pip into virtualenv
import jinja2

# import the helper utility module
from cesm_utils import cesmEnvLib

# import the MPI related modules
from asaptools import partition
#from asaptools import simplecomm, vprinter, timekeeper

# import the diag baseclass module
from ocn_diags_bc import OceanDiagnostic
#from ocn_diags_bc import RecoverableError

# import the plot classes
#from diagnostics.ocn.Plots import ocn_diags_plot_bc
#from diagnostics.ocn.Plots import ocn_diags_plot_factory

if sys.hexversion < 0x02070000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 2.7.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)

class modelVsObsMARBL(OceanDiagnostic):
    """model vs. obs MARBL ocean diagnostics setup
    """
    def __init__(self):
        """ initialize
        """
        super(modelVsObsMARBL, self).__init__()

        self._name = 'MODEL_VS_OBS_MARBL'
        self._title = 'Model vs. Observations MARBL'

    def check_prerequisites(self, env):
        """ check prerequisites
        """
        print("  Checking prerequisites for : {0}".format(self.__class__.__name__))
        super(modelVsObsMARBL, self).check_prerequisites(env)

        # clean out the old working plot files from the workdir
        if env['CLEANUP_FILES'].upper() in ['T', 'TRUE']:
            cesmEnvLib.purge(env['WORKDIR'], '.*\.pro')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.gif')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.dat')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.ps')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.png')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.html')

        return env

    def run_diagnostics(self, env, scomm):
        """ call the necessary plotting routines to generate diagnostics plots
        """
        super(modelVsObsMARBL, self).run_diagnostics(env, scomm)
        scomm.sync()

        # setup some global variables
        requested_plots = list()
        local_requested_plots = list()
        local_html_list = list()

        # define the template_path for all tasks
        template_path = '{0}/diagnostics/diagnostics/ocn/Templates'.format(env['POSTPROCESS_PATH'])

        # all the plot module XML vars start with MVOMARBL_PM_ -- need to strip that off
        for key, value in env.iteritems():
            if (re.search("\AMVOMARBL_PM_", key) and value.upper() in ['T','TRUE']):
                k = key[10:]
                requested_plots.append(k)

        scomm.sync()
        print('model vs. obs MARBL - after scomm.sync requested_plots = {0}'.format(requested_plots))

        if scomm.is_manager():
            print('model vs. obs MARBL - User requested plot modules:')
            print('model vs. obs MARBL - Creating plot html header')
            template_loader = jinja2.FileSystemLoader(searchpath=template_path)
            template_env = jinja2.Environment(loader=template_loader)

            template_file = 'model_vs_obs_MARBL.tmpl'
            print('getting template')
            template = template_env.get_template(template_file)
            print('done getting template')

            # get the current datatime string for the template
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('now = {0}'.format(now))

            # test the template variables
            template_vars = {'casename' : env['CASE'],
                             'username' : env['USER_NAME'],
                             'tagname' : env['CESM_TAG'],
                             'start_year' : env['YEAR0'],
                             'stop_year' : env['YEAR1'],
                             'today': now
                            }

            print('model vs. obs MARBL - Rendering plot html header')
            plot_html = template.render(template_vars)

        scomm.sync()

        print('model vs. obs MARBL - Partition requested plots')
        # partition requested plots to all tasks
        local_requested_plots = scomm.partition(requested_plots, func=partition.EqualStride(), involved=True)
        scomm.sync()

        for requested_plot in local_requested_plots:
            print('model vs obs MARBL - insert code to plot {0} here'.format(requested_plot))
        scomm.sync()

        # define a tag for the MPI collection of all local_html_list variables
        html_msg_tag = 1

        all_html = list()
        all_html = [local_html_list]
        if scomm.get_size() > 1:
            if scomm.is_manager():
                all_html = [local_html_list]

                for num_tasks in range(1, scomm.get_size()):
                    rank, temp_html = scomm.collect(tag=html_msg_tag)
                    all_html.append(temp_html)

            else:
                return_code = scomm.collect(data=local_html_list, tag=html_msg_tag)

        scomm.sync()

        if scomm.is_manager():

            # merge the all_html list of lists into a single list
            all_html = list(itertools.chain.from_iterable(all_html))
            for each_html in all_html:
                #print('each_html = {0}'.format(each_html))
                plot_html += each_html

            print('model vs. obs MARBL - Adding footer html')
            with open('{0}/footer.tmpl'.format(template_path), 'r') as tmpl:
                plot_html += tmpl.read()

            print('model vs. obs MARBL - Writing plot index.html')
            with open('{0}/index.html'.format(env['WORKDIR']), 'w') as index:
                index.write(plot_html)

            print('*************************************************************************************')
            print('Successfully completed generating ocean diagnostics model vs. observation MARBL plots')
            print('*************************************************************************************')

        scomm.sync()

        # append the web_dir location to the env
        key = 'OCNDIAG_WEBDIR_{0}'.format(self._name)
        env[key] = env['WORKDIR']

        return env
