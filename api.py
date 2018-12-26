# -×- coding:utf-8 -*-
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json
import os
import base64
import logging.handlers
import threading
from routersploit import interpreter
from routersploit.core.exploit import utils

log_handler = logging.handlers.RotatingFileHandler(
    filename='/log/framework.log', maxBytes=500000)
log_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s       %(message)s')
log_handler.setFormatter(log_formatter)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(log_handler)

app = Flask(__name__, root_path=".")

CURRNET_SESSHDLR = None
THREAD_LIST = []


###
# All API definition
###
@app.route('/allcounts', methods=['GET', 'POST'])
def allcounts(self):
    # Get all vulnerable statics in last year
    error = None
    if request.method == "POST":
        return None


@app.route('/newvuls', methods=['GET', 'POST'])
def newvuls(self):
    # Get new vulner statics from testing in last year.
    pass


@app.route('/total', methods=['GET', 'POST'])
def total(self):
    # Get static in total datas
    pass


@app.route('/month', methods=['GET', 'POST'])
def month(self):
    # Get statics by month
    pass

# TODO：Need Error Page with all route ！！！！ Redirect to /, refresh the taskid
###
# Main Page Access
###
@app.route('/testcase', methods=['GET', 'POST'])
def testcase():
    # Make the testcase runner page with parameters GET or POST
    # Iter all modules and load into page.
    case_details = list()
    cases = utils.index_modules()
    cases_op = cases
    for case in cases_op:
        type = str(case.split('.')[1]).upper()
        case_details.append([type, case])

    return render_template("icons.html", cases_details=case_details)


@app.route('/testing', methods=['GET', 'POST'])
def testing():
    # CHECK REFER FIRST!!! Configure test for testing.
    if request.method == 'GET':
        try:
            if request.method == 'GET':
                module = str(request.query_string).split('=')[1]
                # fullpath = 'engine.modules.' + module
                try:
                    # del fullpath
                    print "Cleaning env..."  # Cleaning last module loaded.
                    CURRNET_SESSHDLR.command_action(module)
                except Exception, e:
                    print e.message
                # exp = utils.import_exploit('engine.modules.' + module)
                # print exp.__info__
                # = exp()  # Instance class
                infos = CURRNET_SESSHDLR.module_metadata
                name = infos['Name']
                description = infos['Description']
                devices = infos['Date']
                cves = infos['Covered']
                case_target = CURRNET_SESSHDLR.current_module.target
                case_opt_port = CURRNET_SESSHDLR.current_module.dstport
                case_opt_srcip = CURRNET_SESSHDLR.current_module.source
                case_opt_srcport = CURRNET_SESSHDLR.current_module.srcport
            return render_template("user.html", case_name=name.decode('utf-8'),
                                   case_info_description=description.decode(
                                       'utf-8'),
                                   case_info_devices=devices[0].decode('utf-8'),
                                   case_info_cves=cves[0].decode('utf-8'),
                                   case_target=case_target,
                                   case_opt_port=case_opt_port,
                                   case_opt_srcip=case_opt_srcip,
                                   case_opt_srcport=case_opt_srcport
                                   )
        except IndexError:
            return redirect("/warn?msg=6K+35YWI6YCJ5oup5rWL6K+V55So5L6L")


@app.route('/warn', methods=['GET', 'POST'])
def warn():
    msg = ""
    if request.method == 'GET':
        Emsg = str(request.query_string).split('=')[1]
        msg = base64.b64decode(Emsg)
        return render_template("warn.html", msg=msg.decode('utf-8'))


@app.route('/', methods=['GET', 'POST'])
def index():
    # Start the framework main engine
    # Attention:
    #   All modules load with the main engine start
    #   Load modules which specified by user need interpreter.utils module
    #   Single User Only!!! @ 20181210
    #   TODO: Fix multi-user with threading
    PR = TInterpreter()
    global CURRNET_SESSHDLR
    CURRNET_SESSHDLR = PR
    print CURRNET_SESSHDLR.taskname
    # PR.start()
    # Redirect to dashboard page
    return redirect('/dashboard')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Make the dashboard page
    recents = list()
    vendors = list()
    try:
        e = CURRNET_SESSHDLR.taskname
    except Exception:
        return redirect('/')
    with open('/log/recent.logs', 'r') as recentsfd:
        for line in recentsfd:
            recents.append(line.decode('utf-8'))
    with open('/log/devices.logs', 'r') as devsfd:
        for line in devsfd:
            line = line.decode('utf-8')
            dat = line.split(',')
            vendors.append(
                {"vendor": dat[0], "models": dat[1], "version": dat[2],
                 "exp": dat[3]}
            )
    return render_template("dashboard.html", recents=recents[-8:],
                           vendors=vendors[-8:], tid=CURRNET_SESSHDLR.taskname)


###
# Testing runner
###
@app.route('/starter', methods=['POST'])
def starter():
    # Start a testcase
    # Add details into file
    if request.method == 'POST':
        target = request.form['target']
        port = request.form['port']
        srcip = request.form['srcip']
        srcport = request.form['srcport']
        desc = request.form['desc']
        model = request.form['model']
        ver = request.form['version']
        print request
        country = request.form['country']
        CURRNET_SESSHDLR.command_set('target ' + target)
        CURRNET_SESSHDLR.command_set('dstport ' + port)
        CURRNET_SESSHDLR.command_set('source ' + srcip)
        CURRNET_SESSHDLR.command_set('srcport ' + srcport)
        CURRNET_SESSHDLR._show_options()
        with open('/log/recent.logs', 'w+') as f:
            f.write("Running " + str(target) + " 的 "
                    + CURRNET_SESSHDLR.current_module.__class__.__name__ +
                    "Test")
        with open('/log/devices.logs', 'w+') as f:
            f.write(desc + "," + model + "," + ver + ",-1")
            # TODO: Fix, No Report! Vuls counts is flaw.
        THREAD_LIST.append(CURRNET_SESSHDLR.current_module.run())
        try:
            for t in THREAD_LIST:
                t.start()
        except Exception:
            notify_str = "Something Wrong, Check your settings"
        notify_str = "Started!<br/> - Enjoy the awesome framework!。"
        return notify_str


@app.route('/validator', methods=['POST'])
def validator():
    if request.method == 'POST':
        idx = request.form['idx']
        status = CURRNET_SESSHDLR.current_module.session.test_case_data(
            index=idx)
        print status
        return status


# Pause
## Using Boofuzz API
@app.route('/pause', methods=['POST'])
def pause():
    pass


# Stop
## Using Boofuzz API
@app.route('/stop', methods=['POST'])
def stop():
    os.system("restart")  # Aha! Just a joke! 
    #TODO: Need a framework running wrapper.
    notify_str = "Stopped<br/> - Waiting for restart!"
    return notify_str


if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
