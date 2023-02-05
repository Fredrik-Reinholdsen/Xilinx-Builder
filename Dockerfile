FROM ubuntu:lunar

WORKDIR /f4pga

ENV TZ=Europe/Stockholm
ENV ALLOW_ROOT=true
ENV XRAY_DIR=/f4pga/prjxray
ENV XRAY_UTILS_DIR=/f4pga/prjxray/utils
ENV XRAY_DATABASE_DIR=/f4pga/nextpnr-xilinx/xilinx/external/prjxray-db
ENV NEXTPNR_XILINX=/f4pga/nextpnr-xilinx

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN apt-get update && apt-get install -y git virtualenv \
  python3 python3-pip python3-yaml cmake yosys libboost-all-dev libeigen3-dev

# Clone the project X-ray repository
RUN git clone https://github.com/f4pga/prjxray.git

# Copy modified project X-ray files into repository
COPY CMakeLists.txt /f4pga/prjxray/CMakeLists.txt 
COPY update_parts.py /f4pga/prjxray/utils/update_parts.py
COPY update_resources.py /f4pga/prjxray/utils/update_resources.py
COPY environment.sh /f4pga/prjxray/utils/environment.sh
COPY build_verilog.py /f4pga/build_verilog.py

# Install components and build
RUN cd prjxray; git submodule update --init --recursive; \
  make build; \
  pip3 install -r requirements.txt; \
  pip3 install click

# Clone the nextpnr-xilinx repository and build it
RUN cd /f4pga; \
	git clone https://github.com/gatecat/nextpnr-xilinx.git; \
	cd nextpnr-xilinx; \
	git submodule init; git submodule update; \
	cd xilinx/external; rm -r prjxray-db; \
  git clone https://github.com/f4pga/prjxray-db.git; cd /f4pga/nextpnr-xilinx; \
	cmake -DARCH=xilinx -D BUILD_GUI=OFF .; \
	make

# Build part databases
RUN cd /f4pga/nextpnr-xilinx; \
	python3 xilinx/python/bbaexport.py --device xc7z020clg400-1 --bba xilinx/xc7z020.bba; \
	./bbasm --l xilinx/xc7z020.bba xilinx/xc7z020.bin; \
	python3 xilinx/python/bbaexport.py --device xc7a35tcsg324-1 --bba xilinx/xc7a35t.bba; \
	./bbasm --l xilinx/xc7a35t.bba xilinx/xc7a35t.bin

ENTRYPOINT ["python3", "/f4pga/build_verilog.py"]
