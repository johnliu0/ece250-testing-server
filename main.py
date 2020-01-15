import os
import subprocess
import uuid
import shutil
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_DIR'] = os.path.expanduser('~/ece250_data')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
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

    # feed test case into program
    test_case_in = subprocess.Popen(
        ['cat', os.path.join('testcases', 'p0', 'test01.in')],
        universal_newlines=True,
        stdout=subprocess.PIPE)
    test_case_in.wait()
    test_process = subprocess.Popen(
        './a.out',
        shell=True,
        cwd=temp_dir,
        stdin=test_case_in.stdout,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    test_process.wait()

    # compare program output to test case output
    expected_output = []
    actual_output = []
    success = True
    with open(os.path.join('testcases', 'p0', 'test01.out')) as test_case_out:
        # iterate through each line in test case and program output
        prog_output = test_process.stdout
        while True:
            test_case_line = test_case_out.readline()
            prog_output_line = prog_output.readline()
            if test_case_line == '' and prog_output_line == '':
                break
            if test_case_line != prog_output_line:
                success = False
            expected_output.append(test_case_line)
            actual_output.append(prog_output_line)

    # remove temp dir and its contents
    shutil.rmtree(temp_dir)

    return render_template(
        'testcase.html',
        expected=expected_output,
        actual=actual_output,
        success=success)
