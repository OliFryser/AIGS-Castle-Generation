import random
import sys


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: python generate_numbers.py <width> <height> <max_height> <output_file>"
        )
        sys.exit(1)

    try:
        width = int(sys.argv[1])
        height = int(sys.argv[2])
        max_height = int(sys.argv[3])
        output_file = sys.argv[4]
    except ValueError:
        print("width, height and max_height must be integers.")
        sys.exit(1)

    with open(output_file, "w") as f:
        line = f"{width} {height} {max_height}"
        f.write(line + "\n")
        for _ in range(height):
            line = " ".join(str(random.randint(0, 2)) for _ in range(width))
            f.write(line + "\n")

    print(
        f"File '{output_file}' generated with {height} lines and {width} numbers per line."
    )


if __name__ == "__main__":
    main()
