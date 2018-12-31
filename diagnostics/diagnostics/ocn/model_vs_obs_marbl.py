""" Wrapper for yet-to-be-written MARBL diagnostic package

Based on model_vs_obs_ecosys.py, the wrapper to Ivan Lima's python scripts
"""
from __future__ import print_function

# import core python modules
import datetime
#import errno
#import glob
import itertools
import os
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

        # import marbl-diags (replace this with importlib?)
        sys.path.append(os.path.join(env['POSTPROCESS_PATH'], 'ocn_diag', 'marbl-diags'))
        import marbl_diags
        # FIXME: config_key = casename? and config_dict based on XML vars? var_dict from YAML?
        config_key = 'climo state plots'
        config_dict = dict()
        config_dict[config_key] = dict()
        config_dict[config_key]['short_name'] = config_key
        config_dict[config_key]['description'] = 'MARBL diagnostics from a CESM run'
        config_dict[config_key]['dirout'] = env['WORKDIR']
        config_dict[config_key]['source'] = 'ocean_diagnostics'
        config_dict[config_key]['grid'] = 'POP_gx1v7'
        config_dict[config_key]['operations'] = ['plot_climo']
        # FIXME: don't hard-code variable list!
        #        Also need to map from POP varname to general name -- NO3 -> nitrate
        config_dict[config_key]['variable_list'] = ['nitrate']
        config_dict[config_key]['depth_list'] = [0.]
        config_dict[config_key]['cache_data'] = False
        config_dict[config_key]['data_sources'] = dict()
        config_dict[config_key]['data_sources']['cesm_out'] = dict()
        config_dict[config_key]['data_sources']['cesm_out']['source'] = 'cesm'
        config_dict[config_key]['data_sources']['cesm_out']['open_dataset'] = dict()
        config_dict[config_key]['data_sources']['cesm_out']['open_dataset']['filetype'] = 'climo'
        # FIXME: Get dirin from XML
        config_dict[config_key]['data_sources']['cesm_out']['open_dataset']['dirin'] = '/glade/scratch/mlevy/archive/c.e21.C1850ECO.T62_g17.test_postprocessing/ocn/proc/climo.1.3'
        config_dict[config_key]['data_sources']['cesm_out']['open_dataset']['case'] = 'CASENAME'
        config_dict[config_key]['data_sources']['cesm_out']['open_dataset']['stream'] = 'mavg'
        # Get datestr from XML
        config_dict[config_key]['data_sources']['cesm_out']['open_dataset']['datestr'] = '0001-0003'
        var_dict = dict()
        var_dict['nitrate'] = dict()
        var_dict['nitrate']['plot_units'] = 'mmol/m^3'
        var_dict['nitrate']['contours'] = dict()
        var_dict['nitrate']['contours']['levels'] = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1, 1.5, 2, 4, 6, 8, 10, 12, 14,
                                                     16, 18, 20, 22, 24, 26, 28, 30, 34, 38, 42]
        var_dict['nitrate']['contours']['midpoint'] = 2
        var_dict['nitrate']['contours']['extend'] = 'both'
        var_dict['nitrate']['contours']['cmap'] = 'PRGn'

        # FIXME: need to figure out how to parallelize this!
        # Ideally by looping over variables and setting config_dict[config_key]['variable_list']?
        tmp = marbl_diags.AnalysisElements(config_key, config_dict[config_key], var_dict)
        tmp.do_analysis()

        # define the template_path for all tasks
        template_path = '{0}/diagnostics/diagnostics/ocn/Templates'.format(env['POSTPROCESS_PATH'])

        # all the plot module XML vars start with MVOMARBL_PM_ -- need to strip that off
        for key, value in env.iteritems():
            # FIXME: auto-gen MVOMARBL_PM_ xml variables?
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
