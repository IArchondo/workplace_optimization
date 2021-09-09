from pathlib import Path


class Directories:
    def __init__(self):
        self.CONFIG = Path("wp_opti/config/config.yaml")
        self.INPUT_SAMPLE_DATA = Path("input_sample_data")


directories = Directories()
