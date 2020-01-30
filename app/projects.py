from typing import List
import os
import subprocess
from subprocess import TimeoutExpired
import uuid
import shutil
import tarfile
from datetime import datetime
from flask import (
    Blueprint,
    current_app as flask_app,
    render_template,
    request,
    g)
from werkzeug.utils import secure_filename
from models.user import User
from models.submission import Submission

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/<project_num>', methods=['GET', 'POST'])
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
        if g.auth['isAuthenticated']:
            user = User.objects.get({ 'email': g.auth['user']['email'] })
            return render_template('project.html',
                project_num=project_num,
                submissions=user.submissions)
        else:
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
        if (is_file_ext_valid(filename, ['.gz', '.cpp', '.h', '.hpp'])
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
                if (is_file_ext_valid(file.name, ['.cpp', '.h', '.hpp'])
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
    test_case_num = 0
    num_testcases = len(test_case_files)
    num_passed = 0
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
        test_case_num += 1

        # attempt to run the testcase with a time limit of 0.1s
        try:
            test_process.wait(timeout=0.1)
        except TimeoutExpired as e:
            test_case_data.append(TestCaseData(
                num=test_case_num, success=False, timed_out=True))
            continue
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
                    if success:
                        num_passed += 1
                    break
                if test_case_line != prog_output_line:
                    success = False
                expected_output_lines.append(test_case_line)
                actual_output_lines.append(prog_output_line)
        test_case_data.append(TestCaseData(
            num=test_case_num, success=True,
            expected=expected_output_lines,
            actual=actual_output_lines))
    clean_temp_dir()

    # save submission if user is logged in
    if g.auth['isAuthenticated']:
        submission = Submission(
            created_date=datetime.now(),
            num_testcases=num_testcases,
            num_passed=num_passed,
            num_failed=num_testcases-num_passed).save()
        user = User.objects.get({ 'email': g.auth['user']['email'] })
        user.submissions.append(submission)
        user.save()

    return render_template(
        'testcases.html',
        test_cases=test_case_data,
        all_passed=num_passed==num_testcases)


class TestCaseData:
    """Holds information about a test case."""

    def __init__(self,
                 num: int,
                 success: bool,
                 expected: List[str]=[],
                 actual: List[str]=[],
                 timed_out: bool=False):
        self.num = num
        self.success = success
        self.expected = expected
        self.actual = actual
        self.timed_out = timed_out
