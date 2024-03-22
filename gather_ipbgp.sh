#!/bin/bash

base_dir=/home/student/mini_internet_project/groups

read -p "Enter Number: " n
n=${n:-50}
mkdir -p /home/student/ipbgp

for ((x=1; x<=n; x++))
do
	src_file="$base_dir/g$x/RTRA/looking_glass.txt"
	dest_file=/home/student/ipbgp/$x.txt
	if [[ -f "$src_file" ]]; then
		
		cp "$src_file" "$dest_file"
		echo "Copied $src_file to $dest_file"
	else
		echo "Source file $src_file not found."
	fi
done
echo "All files copied to ~/ipbgp/"
