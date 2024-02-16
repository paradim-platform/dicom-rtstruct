from typing import List

import pydicom
from pydicom.uid import generate_uid

from .dicom import apply_metadata, make_file_meta


def make_rtstruct(ref_dicoms: List[pydicom.FileDataset]) -> pydicom.FileDataset:
    # Inspired by https://pydicom.github.io/pydicom/stable/auto_examples/input_output/plot_write_dicom.html
    rtstruct_class_uid = '1.2.840.10008.5.1.4.1.1.481.3'
    instance_uid = generate_uid()

    file_meta = make_file_meta(sop_class_uid=rtstruct_class_uid, sop_instance_uid=instance_uid)

    # Create the DICOM Dataset
    rtstruct = pydicom.FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Set the transfer syntax
    rtstruct.is_little_endian = True
    rtstruct.is_implicit_VR = True

    rtstruct.SOPClassUID = rtstruct_class_uid
    rtstruct.SOPInstanceUID = instance_uid

    rtstruct = apply_metadata(rtstruct, ref_dicoms[0])

    # TODO: add rtstruct related data

    return rtstruct


