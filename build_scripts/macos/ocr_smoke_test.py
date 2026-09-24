"""Smoke-test ddddocr on the current architecture.

Upstream max32002/tixcraft_bot#82: captcha OCR silently fails on ARM, so a
successful pip install proves nothing. Renders an image and requires non-empty
text back (accuracy is not checked). Checks the host interpreter only; the
frozen bundle is checked by build_local.py via --self-test.

Exit code 0 means the OCR stack is usable on this architecture.
"""

import platform
import sys


def main():
    print("platform.machine():", platform.machine())
    print("sys.platform:", sys.platform)

    import ddddocr
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (120, 40), color="white")
    ImageDraw.Draw(image).text((8, 4), "A1B2", fill="black",
                               font=ImageFont.load_default(size=28))

    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    ocr = ddddocr.DdddOcr(show_ad=False)
    result = ocr.classification(buffer.getvalue())

    print("ddddocr returned:", repr(result))
    if not isinstance(result, str) or not result.strip():
        raise SystemExit("ddddocr returned no text; OCR stack is broken")

    print("OCR smoke test passed on", platform.machine())


if __name__ == "__main__":
    main()
