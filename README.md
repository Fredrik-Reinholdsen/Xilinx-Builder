# Xilinx-Builder
Build Xilinx FPGA bitstreams with ease. 

A Docker image and python script that uses the F4PGA toolchain and nextpnr-xilinx to build bitstreams for the Artix 7 xc7a35t and Zynq 7 xc7z020 FPGAs.
With some relativley minor modifications you can make images can to build bitstreams for most Xilinx Series 7 FGPAs.
The image uses the [yosys](https://github.com/YosysHQ/yosys), [F4PGA Toolchain](https://f4pga.org/),
[Project X-ray](https://github.com/f4pga/prjxray) and [nextpnr-xilinx](https://github.com/gatecat/nextpnr-xilinx) to synthesize and place-and-route and build bitstreams.

## Prerequisite
A working Docker installation is needed to build and run the image.

## Installation
Clone the repository and `cd` into it. When standing in the repository root, run:

```bash
docker build . -t xilinx_builder
```

to build the image.  
*NOTE* - The build time for this container is quite long.


## Run
The entrypoint takes two arguments, a *.v* top-module verilog source file, and an *.xdc* constraints file. 
You can also add a `--part` argument to specify which FPGA part you would like to build for. 
Fruthermore, one can also add a `--build-dir` option to specify a directory for all of the built output files, default is *./build*

The two supported FPGAs are the Xilinx xc7a35tcsg324-1 Aritx 7 (Same as that on the Arty-A35 board), and the Xilinx xc7z020clg400-1 Zynq 7 FGPA (same as that on the Arty-Z20 and Pynq-Z2 board).
The Dockerfile can be modified to support other parts. The reason I did not add support for more parts out of the box is the very long database build times for each part.
By default the xc7a35tcsg324-1 part will be used.

To build a bitstream from a verilog source file `top.v` using constraints specified by `constraints.xdc`, run:

```bash
docker run -v $(pwd):/io -w /io --rm -it xilinx_builder top.v constraints.xdc --part xc7a35tcsg324-1
```
