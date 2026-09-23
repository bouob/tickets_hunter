"""Smoke-test ddddocr on the current architecture.

Upstream max32002/tixcraft_bot#82 reports that captcha OCR silently fails on
ARM machines, so a green "pip install succeeded" is not evidence that OCR
works. This renders a throwaway image and asks ddddocr to read it. The test
asserts that the model loads and returns a string, not that the string is
correct - recognition accuracy is the model's job, not the build's.

Exit code 0 means the OCR stack is usable on this architecture.
"""

import platform
import sys


def main():
    print("platform.machine():", platform.machine())
    print("sys.platform:", sys.platform)

    import ddddocr
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (120, 40), color="white")
    ImageDraw.Draw(image).text((12, 12), "A1B2", fill="black")

    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    ocr = ddddocr.DdddOcr(show_ad=False)
    result = ocr.classification(buffer.getvalue())

    print("ddddocr returned:", repr(result))
    if not isinstance(result, str):
        raise SystemExit("ddddocr did not return a string; OCR stack is broken")

    print("OCR smoke test passed on", platform.machine())


if __name__ == "__main__":
    main()
