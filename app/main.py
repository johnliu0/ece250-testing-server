# ECE250 Testing Server
# For the Winter 2020 term.
# Author: John Liu

import os
import subprocess
import uuid
import shutil
import tarfile
import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session)
from werkzeug.utils import secure_filename

import app.db as db
import app.auth as auth

"""Entry point for app."""
logging.basicConfig(filename='logs.txt')
flask_app = Flask(__name__)
flask_app.config.from_envvar('CFG_FILE')
# directory for where temporary files will be placed
flask_app.config['UPLOAD_DIR'] = os.path.expanduser('~')
flask_app.register_blueprint(auth.bp)
db.init()

@flask_app.route('/')
def index():
    """
    Homepage.
    """

    return render_template('index.html', auth=session.get('auth', {}))

@flask_app.route('/projects/<project_num>', methods=['GET', 'POST'])
def projects(project_num):
    """
    Endpoint project testing page.
    """

    try:
        # try to convert project_num to integer
        project_num = int(project_num)
        if project_num < 0 or project_num > 1:
            raise
    except:
        return f'Project {project_num} does not exist'

    if request.method == 'GET':
        return render_template('project.html', project_num=project_num)

    if 'src' not in request.files:
        return 'name of files should be src'

    # generate a temporary unique folder for file upload
    temp_dir_name = str(uuid.uuid1())
    temp_dir = os.path.join(flask_app.config['UPLOAD_DIR'], temp_dir_name)
    os.mkdir(temp_dir)

    # remove temp dir and its contents
    def clean_temp_dir():
        shutil.rmtree(temp_dir)

    # check if a file has an allowed extension
    def is_file_ext_valid(filename, allowed_extensions):
        idx_dot = filename.rfind('.')
        return idx_dot != -1 and filename[idx_dot:].lower() in allowed_extensions

    # save all uploaded files to temp folder
    uploaded_files = request.files.getlist('src')
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        # allow .gz, .cpp, and .h files, and makefile
        if (is_file_ext_valid(filename, ['.gz', '.cpp', '.h'])
            or filename.lower() == 'makefile'):
            file.save(os.path.join(temp_dir, filename))

    # if one file was uploaded, the user should be trying to
    # upload a .tar.gz containing their source code
    if len(uploaded_files) == 1:
        try:
            tarfile_path = os.path.join(temp_dir, secure_filename(uploaded_files[0].filename))
            # check if the file is valid; is_tarfile returns a boolean and may raise an exception
            if not tarfile.is_tarfile(tarfile_path):
                raise
            tar_obj = tarfile.open(tarfile_path)
            # extract all .cpp, .h, files and makefile from tar
            valid_files = []
            for file in tar_obj.getmembers():
                # do not allow malicious file names
                if file.name != secure_filename(file.name):
                    continue
                if (is_file_ext_valid(file.name, ['.cpp', '.h'])
                    or file.name.lower() == 'makefile'):
                    valid_files.append(file)

            # extract tar to temp dir
            tar_obj.extractall(path=temp_dir, members=valid_files)
        except Exception as e:
            clean_temp_dir()
            return 'invalid .tar.gz'

    # run make
    make_process = subprocess.Popen(
        'make',
        shell=True,
        cwd=temp_dir,
        universal_newlines=True,
        stderr=subprocess.PIPE)
    make_process.wait()

    # check for compilation error
    if make_process.returncode != 0:
        clean_temp_dir()
        stderr = make_process.stderr
        err = []
        while True:
            err_line = stderr.readline()
            if err_line == '':
                break
            err.append(err_line)
        return render_template(
            'compilefail.html',
            error=err)

    # computes an array of (testXX.in, testXX.out) pairs.
    def get_testcases_for_project(project):
        p = os.path.join('ECE250-testCases', project)
        files = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
        files.sort()
        ret = []
        if len(files) % 2 != 0:
            return ret
        it = iter(files)
        for curr in it:
            ret.append((curr, next(it)))
        return ret

    # get name of project; this should also be the name of the folder
    # where the relevant test cases are
    project_name = f'p{project_num}'

    # names of the executables for the projects, where the index of the
    # executable is the project number
    executable_names = ['playlistdriver', 'dequedriver'];

    # iterate through each test case and compare with program output
    test_case_data = []
    test_case_files = get_testcases_for_project(project_name)
    test_case_num = 1
    all_passed = True
    for test_case_in_file, test_case_out_file in test_case_files:
        # pipe testcase to program
        test_case_in = subprocess.Popen(
            ['cat', os.path.join('ECE250-testCases', project_name, test_case_in_file)],
            universal_newlines=True,
            stdout=subprocess.PIPE)
        test_case_in.wait()
        test_process = subprocess.Popen(
            f'./{executable_names[project_num]}',
            shell=True,
            cwd=temp_dir,
            stdin=test_case_in.stdout,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        test_process.wait()
        prog_output = test_process.stdout

        expected_output_lines = []
        actual_output_lines = []
        success = True
        with open(os.path.join('ECE250-testCases', project_name, test_case_out_file)) as test_case_out:
            # compare test case output and program output line by line
            while True:
                test_case_line = test_case_out.readline()
                prog_output_line = prog_output.readline()
                if test_case_line == '' and prog_output_line == '':
                    break
                if test_case_line != prog_output_line:
                    success = False
                    all_passed = False
                expected_output_lines.append(test_case_line)
                actual_output_lines.append(prog_output_line)
        test_case_data.append((test_case_num, expected_output_lines, actual_output_lines, success))
        test_case_num += 1

    clean_temp_dir()

    return render_template(
        'testcases.html',
        test_cases=test_case_data,
        all_passed=all_passed)
