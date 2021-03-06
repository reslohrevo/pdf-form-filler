"""
Test for Foo
"""
from mock import mock_open, patch, MagicMock
import pytest
import json
import os
import sys
from io import BytesIO
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from filler import FormRenderer

@pytest.fixture
def v1_form_data():
    """
    V1 Form data fixtures.
    """
    return """
    [
        {
            "comment": "This thing.",
            "page": 1,
            "x": 137,
            "y": 111,
            "width": 400,
            "height": 50,
            "align_horizontal": "center",
            "align_vertical": "center",
            "font_face": "Courier",
            "font_size": 24,
            "text": "This Thing"
        },
        {
            "comment": "That thing.",
            "page": 2,
            "x": 337,
            "y": 511,
            "width": 100,
            "height": 100,
            "align_horizontal": "right",
            "align_vertical": "center",
            "font_face": "Courier",
            "font_size": 14,
            "text": "image.jpg"
        }
    ] """


@pytest.fixture
def v2_form_data():
    """
    V2 Form data fixtures. Adds `type' and renames `text' to `data' while still
    permitting `text'.
    """
    return """
    [
        {
            "comment": "This thing.",
            "page": 1,
            "x": 137,
            "y": 111,
            "type": "text",
            "width": 400,
            "height": 50,
            "align_horizontal": "center",
            "align_vertical": "center",
            "font_face": "Courier",
            "font_size": 24,
            "text": "This Thing"
        },
        {
            "comment": "That thing.",
            "page": 2,
            "x": 337,
            "y": 511,
            "type": "image",
            "width": 100,
            "height": 100,
            "align_horizontal": "right",
            "align_vertical": "center",
            "font_face": "Courier",
            "font_size": 14,
            "data": "image.jpg"
        }
    ] """


@pytest.fixture
def v3_form_data():
    """
    V3 Form data fixture. Adds `font_color' and `rotation'. Maintains compat
    with their absence.
    """
    # TODO: Add another field with missing `font_color' and `rotation' for test.
    return """
    [
        {
            "comment": "This thing.",
            "page": 1,
            "x": 137,
            "y": 111,
            "type": "text",
            "width": 400,
            "height": 50,
            "align_horizontal": "center",
            "align_vertical": "center",
            "font_face": "Courier",
            "font_size": 24,
            "font_color": "0000FF",
            "rotation": 0,
            "data": "This Thing"
        },
        {
            "comment": "That thing.",
            "page": 2,
            "x": 337,
            "y": 511,
            "type": "image",
            "width": 100,
            "height": 100,
            "align_horizontal": "right",
            "align_vertical": "center",
            "font_face": "Courier",
            "font_size": 14,
            "font_color": "000000",
            "rotation": 45,
            "data": "image.jpg"
        }
    ] """

class TestFormRendererInitialization(object):
    """
    Class instantiation tests.
    """

    def test_basic_attrs(self, v3_form_data):
        """
        Test basic attributes.
        """
        base_form = "base_form.pdf"
        output_file = "output_file.pdf"

        mo = mock_open(read_data=v3_form_data)
        with patch('builtins.open', mo, create=True):
            fr = FormRenderer(base_form, v3_form_data, output_file)
            assert fr.base_form == base_form
            assert fr.output_file == output_file
            assert fr.preview == None

    def test_form_data(self, v3_form_data):
        """
        Test form data. Read form data. Confirm identical.
        """
        mo = mock_open(read_data=v3_form_data)
        with patch('builtins.open', mo, create=True):
            fr = FormRenderer("base_form.pdf", "form_data.json",
                    "output_form.pdf")
            data = json.loads(v3_form_data)
            fields = [x for x in data]
            fields.sort(key=lambda x: x['page'], reverse=False)
            assert fr.fields == fields

    def test_extra_data(self, v3_form_data):
        """
        Test extra data. Combine form data and extra data. Confirm identical.
        """
        mo = mock_open(read_data=v3_form_data)
        with patch('builtins.open', mo, create=True):
            fr = FormRenderer("base_form.pdf", "form_data.json",
                    "output_form.pdf", "extra_data.json")
            data = json.loads(v3_form_data)
            fields = [x for x in data] + [x for x in data]
            fields.sort(key=lambda x: x['page'], reverse=False)
            assert fr.fields == fields

@patch('filler.PdfFileReader')
@patch('filler.PdfFileWriter')
@patch('filler.FormRenderer.render_field')
class TestFormRendererRenderMethod(object):
    """
    Test the render() method.
    """
    def test_render(self, mock_render_field, mock_pdf_wrt, mock_pdf_rdr, v3_form_data):
        """
        Test render method. Rough. Looks like it will inspire method refactor.
        Merely assert that render_field() called twice.
        """
        class Rdr(object):
            getNumPages = MagicMock(return_value=2)
            getPage = MagicMock()

        mo = mock_open(read_data=v3_form_data)
        with patch('builtins.open', mo, create=True):
            fr = FormRenderer("base_form.pdf", "form_data.json",
                    "output_form.pdf")

        mock_pdf_rdr.return_value = Rdr()
        with patch('builtins.open', mock_open(read_data=b'0'), create=True):
            fr.render()

        assert mock_render_field.call_count == 2

