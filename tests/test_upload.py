from pages.upload import UploadPage


def test_create_palette_sends_hex_strings_to_shared_palette():
    upload = UploadPage.__new__(UploadPage)
    upload.picked = [
        {"hex": "#123456", "rgb": [18, 52, 86], "source": "click"},
        {"hex": "#abcdef", "rgb": [171, 205, 239], "source": "auto"},
    ]
    received = []
    upload.on_create_palette = received.append

    upload.create_palette()

    assert received == [["#123456", "#abcdef"]]