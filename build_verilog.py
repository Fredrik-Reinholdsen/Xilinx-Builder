import click
import pathlib
import os
import subprocess

ALLOWED_PARTS = ["xc7z020clg400-1", "xc7a35tcsg324-1"]

ENV = os.environ.copy()


def run_cmd(cmd):
    """Runs a command and checks its return code for failiure."""
    rc = subprocess.run(cmd, shell=True, env=ENV)
    rc.check_returncode()


def shell_source(script):
    pipe = subprocess.Popen(". %s; env" %
                            script, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")
    output = pipe.communicate()[0].decode()
    env = dict((line.split("=", 1) for line in output.splitlines()))
    ENV.update(env)


@click.command()
@click.argument("verilog_file", type=click.Path(exists=True))
@ click.argument("xdg_file", type=click.Path(exists=True))
@ click.option('--part', default="xc7a35tcsg324-1", help=f"Which Xilinx part to use. Must be one of: {ALLOWED_PARTS}")
@ click.option('--build-dir', default="build", help="Directory where build files are generated.")
def cli(verilog_file, xdg_file, part="xc7a35tcsg324-1", build_dir="build"):
    if not os.path.exists(f"./{build_dir}"):
        os.mkdir(f"{build_dir}")

    verilog_file = pathlib.Path(verilog_file)
    xdc_file = pathlib.Path(xdg_file)

    if part == "xc7a35tcsg324-1":
        bin_name = "xc7a35t.bin"
        model = "artix7"
    elif part == "xc7z020clg400-1":
        bin_name = "xc7z020.bin"
        model = "zynq7"
    else:
        click.echo(
            f"ERROR - Unknown part provided! The allowed parts are: {ALLOWED_PARTS}")

    if not os.path.exists(f"{build_dir}"):
        os.mkdir(f"{build_dir}")

    verilog_name = verilog_file.name.split(".")[0]

    run_cmd(
        [f"yosys -p \"synth_xilinx -flatten -abc9 -nobram -arch xc7 -top top; write_json {verilog_name}.json\" {verilog_name}.v"])

    run_cmd(" ".join([
        "${NEXTPNR_XILINX}/nextpnr-xilinx",
        "".join(["--chipdb ${NEXTPNR_XILINX}", f"/xilinx/{bin_name}"]),
        f"--xdc {xdc_file} --json {verilog_name}.json --write {build_dir}/{verilog_name}_routed.json --fasm {build_dir}/{verilog_name}.fasm"
    ]))

    shell_source("${XRAY_DIR}/utils/environment.sh")

    run_cmd(" ".join([
        "${XRAY_UTILS_DIR}/fasm2frames.py --part", f"{part}",
        "--db-root",
        "".join(["${XRAY_DATABASE_DIR}/", f"{model}"]
                ), f"{build_dir}/{verilog_name}.fasm > {build_dir}/{verilog_name}.frames"
    ]))

    run_cmd(" ".join([
        "${XRAY_TOOLS_DIR}/xc7frames2bit --part_file",
        "".join(["${XRAY_DATABASE_DIR}/", f"{model}/{part}/part.yaml"]),
        f"--part_name {part} --frm_file {build_dir}/{verilog_name}.frames --output_file {build_dir}/{verilog_name}.bit"]))

    # Move the json file into the build dir as well
    os.replace(f"{verilog_name}.json", f"{build_dir}/{verilog_name}.json")


if __name__ == "__main__":
    cli()
