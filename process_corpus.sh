for file in `find ../../reddit_data -type f`; do
    echo "Processing $file"
    out_file_name=reddit_data_chains/$(basename $file)
    log_file_name=${out_file_name}.log
    python extract_conversations.py < $file 1>$out_file_name 2>$log_file_name
done
