for file in `find ../../reddit_data -type f`; do
    out_file_name=reddit_filtered/$(basename $file)
    log_file_name=${out_file_name}.log
    nohup python filter_size.py < $file 1>$out_file_name 2>$log_file_name &
done
