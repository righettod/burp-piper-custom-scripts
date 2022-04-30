import json
import subprocess  # nosec B404
"""
Test suites in charge of testing all the scripts based on the expectation defined in file "test_scripts.json"
for the 2 test cases by scripts:
    - The one in which data must be found where the content of the file "[script_name_without_extension]_findcontent.txt" is used as input source
    - The one in which no data must be found where the content of the file "[script_name_without_extension]_findnothing.txt" is used as input source
"""


def __get_property(script_name_without_extension, test_case):
    with open("tests/test_scripts.json", "r") as cfg:
        config = json.load(cfg)
    return config[script_name_without_extension][test_case]


def __get_scripts():
    with open("tests/test_scripts.json", "r") as cfg:
        config = json.load(cfg)
    return config.keys()


def __run_test(test_data_file_name, script_name_without_extension):
    p = subprocess.Popen(["python", f"{script_name_without_extension}.py"], stdin=open(f"tests/{test_data_file_name}"), stdout=subprocess.PIPE)  # nosec B603,B607
    p.wait()
    return (p.returncode, p.stdout.read().decode("utf-8"))


def __check_result(props, rc, content):
    if props["type"] == "Commentators" or props["type"] == "Message viewers":
        marker = props["marker"]
        expected_rc = props["expected-rc"]
        assert rc == expected_rc, f"RC is not equals to {expected_rc} (RC: {rc})"  # nosec B101
        assert marker in content, f"Marker '{marker}' not found in '{content}'"  # nosec B101
    elif props["type"] == "Highlighters":
        expected_rc = props["expected-rc"]
        assert rc == expected_rc, f"RC is not equals to {expected_rc} (RC: {rc})"  # nosec B101


def test_scripts():
    # Get the list of script to tests
    scripts = __get_scripts()
    # Apply test to each of them
    for script in scripts:
        # Apply the 2 test cases
        for test_case in ["findcontent", "findnothing"]:
            print(f"[+] Testing script '{script}' for test case '{test_case}'...")
            # Get test case properties
            props = __get_property(script, test_case)
            # Execute the test case
            rc, content = __run_test(f"{script}_{test_case}.txt", script)
            # Verify the execution result
            __check_result(props, rc, content)
