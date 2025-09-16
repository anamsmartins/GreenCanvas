.PHONY: download-wheels

download-wheels:
	 pip download shapely --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64
	 pip download shapely --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_17_x86_64
	 pip download shapely --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_10_9_x86_64
	 pip download shapely --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64
	 pip download scipy --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux2014_x86_64
	 pip download scipy --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64
	 pip download scipy --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_10_14_x86_64
	 pip download scipy --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_12_0_arm64
