from shell_utils import shell_cmd


def _generate(url):
    # TODO: call submodule
    args = [url, "singlefile.html"]
    cmd = ["single-file"] + args

    return_code, stderr = shell_cmd(cmd)

    if return_code:
        raise Exception(
            f"failed to generate single-file site, return_code: {return_code}. stderr: {stderr}"
        )


def generate_singlefile(url):
    print("generating single-file site...")
    try:
        _generate(url)
    except KeyboardInterrupt:
        print("user interrupted handler, skipping...")
    except Exception as error:
        print(repr(error))
