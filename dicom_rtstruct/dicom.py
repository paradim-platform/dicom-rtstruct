from datetime import datetime

import pydicom
from pydicom.dataset import FileMetaDataset
from pydicom.filebase import DicomBytesIO
from pydicom.uid import PYDICOM_IMPLEMENTATION_UID, generate_uid

from dicom_rtstruct.version import VERSION


def apply_metadata(rtstruct: pydicom.FileDataset, ref_dicom: pydicom.Dataset):
    """See https://dicom.innolitics.com/ciods/rt-struct/"""

    # Patient Layer
    rtstruct.PatientID = ref_dicom.PatientID
    rtstruct.PatientName = ref_dicom.PatientName
    rtstruct.PatientBirthDate = ref_dicom.PatientBirthDate
    rtstruct.PatientSex = ref_dicom.PatientSex

    # Study layer
    rtstruct.StudyDate = ref_dicom.StudyDate
    rtstruct.StudyTime = ref_dicom.StudyTime
    rtstruct.AccessionNumber = ref_dicom.AccessionNumber
    rtstruct.ReferringPhysicianName = ref_dicom.ReferringPhysicianName
    rtstruct.StudyInstanceUID = ref_dicom.StudyInstanceUID
    rtstruct.StudyID = ref_dicom.StudyID
    if 'StudyDescription' in ref_dicom:
        rtstruct.StudyDescription = ref_dicom.StudyDescription
    else:
        rtstruct.StudyDescription = ''

    # Series Layer
    current_date = datetime.now()
    rtstruct.SeriesDate = current_date.strftime('%Y%m%d')
    rtstruct.SeriesTime = current_date.strftime('%H%M%S.%f')  # long format with micro seconds
    rtstruct.Modality = 'RTSTRUCT'
    rtstruct.OperatorsName = ''
    rtstruct.SeriesInstanceUID = generate_uid()
    rtstruct.SeriesNumber = ''

    # Frame of Reference module
    rtstruct.FrameOfReferenceUID = generate_uid()
    rtstruct.PositionReferenceIndicator = ''

    # Instance Layer
    rtstruct.InstanceCreationDate = current_date.strftime('%Y%m%d')
    rtstruct.InstanceCreationTime = current_date.strftime('%H%M%S.%f')  # long format with micro seconds

    # General Equipment module
    rtstruct.Manufacturer = ''
    rtstruct.SoftwareVersions = f'dicom-rtstruct {VERSION}'


def make_file_meta(sop_class_uid: str, sop_instance_uid: str) -> FileMetaDataset:
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationVersion = b'\x00\x01'
    file_meta.MediaStorageSOPClassUID = sop_class_uid
    file_meta.MediaStorageSOPInstanceUID = sop_instance_uid
    file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'

    file_meta.is_little_endian = True
    file_meta.is_implicit_VR = False

    pydicom.dataset.validate_file_meta(file_meta, enforce_standard=True)

    # Write the File Meta Information Group elements
    # first write into a buffer to avoid seeking back, that can be
    # expansive and is not allowed if writing into a zip file
    buffer = DicomBytesIO()
    buffer.is_little_endian = True
    buffer.is_implicit_VR = False
    pydicom.filewriter.write_dataset(buffer, file_meta)

    # CODE FROM THE PYDICOM LIB:
    # If FileMetaInformationGroupLength is present it will be the first written
    #   element, and we must update its value to the correct length.
    # Update the FileMetaInformationGroupLength value, which is the number
    #   of bytes from the end of the FileMetaInformationGroupLength element
    #   to the end of all the File Meta Information elements.
    # FileMetaInformationGroupLength has a VR of 'UL' and so has a value
    #   that is 4 bytes fixed. The total length of when encoded as
    #   Explicit VR must therefore be 12 bytes.
    file_meta.FileMetaInformationGroupLength = buffer.tell() - 12
    del buffer

    return file_meta
