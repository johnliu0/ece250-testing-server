# ECE250 Testing Server
# For the Winter 2020 term.
# Author: John Liu

import os
import subprocess
import uuid
import shutil
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
# directory for where temporary files will be placed
app.config['UPLOAD_DIR'] = os.path.expanduser('~')

@app.route('/')
def index():
    """
    Homepage.
    """

    return render_template('index.html')

@app.route('/upload/<project_num>', methods=['POST'])
def upload_files(project_num):
    """
    Endpoint for receiving source files.
    """

    if project_num != '0':
        return f'Project {project_num} does not exist'

    if 'src' not in request.files:
        return 'name of files should be src'

    # generate a temporary unique folder for file upload
    temp_dir_name = str(uuid.uuid1())
    temp_dir = os.path.join(app.config['UPLOAD_DIR'], temp_dir_name)
    os.mkdir(temp_dir)

    # save all uploaded files to temp folder
    for file in request.files.getlist('src'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(temp_dir, filename))

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
        # remove temp dir and its contents
        shutil.rmtree(temp_dir)
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

    # iterate through each test case and compare with program output
    test_case_data = []
    test_case_files = get_testcases_for_project('p0')
    test_case_num = 1
    all_passed = True
    for test_case_in_file, test_case_out_file in test_case_files:
        # pipe testcase to program
        test_case_in = subprocess.Popen(
            ['cat', os.path.join('ECE250-testCases', 'p0', test_case_in_file)],
            universal_newlines=True,
            stdout=subprocess.PIPE)
        test_case_in.wait()
        test_process = subprocess.Popen(
            './playlistdriver',
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
        with open(os.path.join('ECE250-testCases', 'p0', test_case_out_file)) as test_case_out:
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

    # remove temp dir and its contents
    shutil.rmtree(temp_dir)

    return render_template(
        'testcases.html',
        test_cases=test_case_data,
        all_passed=all_passed)

@app.route('/projects/<project_num>', methods=['GET'])
def projects(project_num):
    """
    Page for uploading source files.
    """

    if project_num != '0':
        return f'Project {project_num} does not exist'
    if project_num == '0':
        return render_template('project.html', project_num=0)
