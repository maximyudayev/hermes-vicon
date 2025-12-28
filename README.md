# HERMES - Vicon

Support package to interface the realtime [Vicon](https://www.vicon.com/) commercial sensing system data in [HERMES](https://github.com/maximyudayev/hermes), through the [DataStream SDK](https://www.vicon.com/software/datastream-sdk/).

## Installation
Node available under the same HERMES namespace of `hermes.vicon` as `ViconProducer`. Download and unarchive the official [DataStream SDK](https://www.vicon.com/software/datastream-sdk/). Install it into the Python environment with:
```bash
pip install <path_to_downloaded_[vicon_dssdk]_folder>
```

### From PyPI
```bash
pip install pysio-hermes-vicon
```

### From source
```bash
git clone https://github.com/maximyudayev/hermes-vicon.git
pip install -e hermes-vicon
```

## Usage
Using the device follows the standard [configuration file specification](https://yudayev.com/hermes) process of HERMES nodes.

Turn on Vicon Nexus desktop application to configure all capturing devices and their names. Fill in those sensor mappings exactly the same way in your HERMES YAML file.

> [!IMPORTANT]
> Ensure the names in Nexus correspond exactly to the mapping in the HERMES config YAML file, [example](https://github.com/maximyudayev/hermes-vicon/blob/main/examples/vicon.yml#L57-L78).

> [!IMPORTANT]
> Currently, `vicon.yml` config file and the `ViconStream` datastructure are only configured for 16-channels analog sEMG signals. Update the stream class manually to capture all other desired data.

## Citation
When using any parts of this repository outside of its intended use, please cite the parent project [HERMES](https://github.com/maximyudayev/hermes).
