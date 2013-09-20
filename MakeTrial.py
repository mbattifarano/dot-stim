from PIL import Image
import ReadStdIn


def main(arg_array):
    args=ReadStdIn.parse(arg_array)
    return 0

if __name__ == '__main__':
    main(sys.argv([1:]))
