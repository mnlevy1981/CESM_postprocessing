from __future__ import print_function

import sys

if sys.hexversion < 0x02070000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 2.7.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)

# import core python modules
import datetime
import errno
import glob
import itertools
import os
import re
import shutil
import traceback

# import modules installed by pip into virtualenv
import jinja2

# import the helper utility module
from cesm_utils import cesmEnvLib
from diag_utils import diagUtilsLib

# import the MPI related modules
from asaptools import partition, simplecomm, vprinter, timekeeper

# import the diag baseclass module
from ocn_diags_bc import OceanDiagnostic

# import the plot classes
from diagnostics.ocn.Plots import ocn_diags_plot_bc
from diagnostics.ocn.Plots import ocn_diags_plot_factory

class modelVsObsEcosys(OceanDiagnostic):
    """model vs. obs ecosys observations ocean diagnostics setup
    """
    def __init__(self):
        """ initialize
        """
        super(modelVsObsEcosys, self).__init__()

        self._name = 'MODEL_VS_OBS_ECOSYS'
        self._title = 'Model vs. Observations Ecosystem'

    def check_prerequisites(self, env):
        """ check prerequisites
        """
        print("  Checking prerequisites for : {0}".format(self.__class__.__name__))
        super(modelVsObsEcosys, self).check_prerequisites(env)

        # clean out the old working plot files from the workdir
        if env['CLEANUP_FILES'].upper() in ['T','TRUE']:
            cesmEnvLib.purge(env['WORKDIR'], '.*\.pro')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.gif')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.dat')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.ps')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.png')
            cesmEnvLib.purge(env['WORKDIR'], '.*\.html')

        # create the plot.dat file in the workdir used by all NCL plotting routines
        diagUtilsLib.create_plot_dat(env['WORKDIR'], env['XYRANGE'], env['DEPTHS'])

        # TODO read in the ecosys_vars.txt file and create the corresponding link files to the climatology files

        return env

    def run_diagnostics(self, env, scomm):
        """ call the necessary plotting routines to generate diagnostics plots
        """
        super(modelVsObsEcosys, self).run_diagnostics(env, scomm)
        scomm.sync()

        # setup some global variables
        requested_plots = list()
        local_requested_plots = list()
        local_html_list = list()

        # define the templatePath for all tasks
        templatePath = '{0}/diagnostics/diagnostics/ocn/Templates'.format(env['POSTPROCESS_PATH']) 

        # all the plot module XML vars start with MVOECOSYS_PM_  need to strip that off
        for key, value in env.iteritems():
            if (re.search("\AMVOECOSYS_PM_", key) and value.upper() in ['T','TRUE']):
                k = key[9:]                
                requested_plots.append(k)

        scomm.sync()
        print('model vs. obs ecosys - after scomm.sync requested_plots = {0}'.format(requested_plots))

        if scomm.is_manager():
            print('model vs. obs ecosys - User requested plot modules:')
            for plot in requested_plots:
                print('  {0}'.format(plot))

            if env['DOWEB'].upper() in ['T','TRUE']:
                
                print('model vs. obs ecosys - Creating plot html header')
                templateLoader = jinja2.FileSystemLoader( searchpath=templatePath )
                templateEnv = jinja2.Environment( loader=templateLoader )
                
                template_file = 'model_vs_obs_ecosys.tmpl'
                template = templateEnv.get_template( template_file )
    
                # get the current datatime string for the template
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # test the template variables
                templateVars = { 'casename' : env['CASE'],
                                 'tagname' : env['CCSM_REPOTAG'],
                                 'start_year' : env['YEAR0'],
                                 'stop_year' : env['YEAR1'],
                                 'today': now
                                 }

                print('model vs. obs ecosys - Rendering plot html header')
                plot_html = template.render( templateVars )

        scomm.sync()

        print('model vs. obs ecosys - Partition requested plots')
        # partition requested plots to all tasks
        local_requested_plots = scomm.partition(requested_plots, func=partition.EqualStride(), involved=True)
        scomm.sync()

        for requested_plot in local_requested_plots:
            try:
                plot = ocn_diags_plot_factory.oceanDiagnosticPlotFactory('obs', requested_plot)

                print('model vs. obs ecosys - Checking prerequisite for {0} on rank {1}'.format(plot.__class__.__name__, scomm.get_rank()))
                plot.check_prerequisites(env)

                print('model vs. obs ecosys - Generating plots for {0} on rank {1}'.format(plot.__class__.__name__, scomm.get_rank()))
                plot.generate_plots(env)

                print('model vs. obs ecosys - Converting plots for {0} on rank {1}'.format(plot.__class__.__name__, scomm.get_rank()))
                plot.convert_plots(env['WORKDIR'], env['IMAGEFORMAT'])

                print('model vs. obs ecosys - Creating HTML for {0} on rank {1}'.format(plot.__class__.__name__, scomm.get_rank()))
                html = plot.get_html(env['WORKDIR'], templatePath, env['IMAGEFORMAT'])
            
                local_html_list.append(str(html))
                #print('local_html_list = {0}'.format(local_html_list))

            except ocn_diags_bc.RecoverableError as e:
                # catch all recoverable errors, print a message and continue.
                print(e)
                print("model vs. obs ecosys - Skipped '{0}' and continuing!".format(request_plot))
            except RuntimeError as e:
                # unrecoverable error, bail!
                print(e)
                return 1

        scomm.sync()

        # define a tag for the MPI collection of all local_html_list variables
        html_msg_tag = 1

        all_html = list()
        all_html = [local_html_list]
        if scomm.get_size() > 1:
            if scomm.is_manager():
                all_html  = [local_html_list]
                
                for n in range(1,scomm.get_size()):
                    rank, temp_html = scomm.collect(tag=html_msg_tag)
                    all_html.append(temp_html)

                #print('all_html = {0}'.format(all_html))
            else:
                return_code = scomm.collect(data=local_html_list, tag=html_msg_tag)

        scomm.sync()
        
        if scomm.is_manager():

            # merge the all_html list of lists into a single list
            all_html = list(itertools.chain.from_iterable(all_html))
            for each_html in all_html:
                #print('each_html = {0}'.format(each_html))
                plot_html += each_html

            print('model vs. obs ecosys - Adding footer html')
            with open('{0}/footer.tmpl'.format(templatePath), 'r+') as tmpl:
                plot_html += tmpl.read()

            print('model vs. obs ecosys - Writing plot index.html')
            with open( '{0}/index.html'.format(env['WORKDIR']), 'w') as index:
                index.write(plot_html)

            if len(env['WEBDIR']) > 0 and len(env['WEBHOST']) > 0 and len(env['WEBLOGIN']) > 0:
                # copy over the files to a remote web server and webdir 
                diagUtilsLib.copy_html_files(env, 'model_vs_obs')
            else:
                print('Model vs. Observations Ecosystme - Web files successfully created in directory:')
                print('{0}'.format(env['WORKDIR']))
                print('The env_diags_ocn.xml variable WEBDIR, WEBHOST, and WEBLOGIN were not set.')
                print('You will need to manually copy the web files to a remote web server.')

            print('*****************************************************************************************')
            print('Successfully completed generating ocean diagnostics model vs. observation ecosystem plots')
            print('*****************************************************************************************')

