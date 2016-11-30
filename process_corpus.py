from sys import argv


def main(in_texts_root, in_result_folder):
    pass


if __name__ == '__main__':
    if len(argv) < 2:
        print 'Usage: {} <root folder> <result folder>'
        exit()
    root_folder, result_folder = argv[1:3]
    main(root_folder, result_folder)
