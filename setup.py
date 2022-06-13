from distutils.core import setup, Extension


def main():
    setup(
        name="dda",
        version="1.0.0",
        description="Functions related to DDA algorithm.",
        ext_modules=[Extension("dda", ["c_code/dda.c"])],
    )


if __name__ == "__main__":
    main()
