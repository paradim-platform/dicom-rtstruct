import pydicom
import pytest
from pydicom.data import get_testdata_file

from dicom_rtstruct import make_rtstruct


@pytest.fixture
def ct() -> pydicom.Dataset:
    return get_testdata_file('CT_small.dcm', read=True)


def test_rtstruct(ct: pydicom.FileDataset):
    ds = make_rtstruct(ref_dicoms=[ct])

    assert ds.Modality
